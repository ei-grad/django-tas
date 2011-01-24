#!/usr/bin/env python
#
# Copyright (c) 2010-2011 Andrew Grigorev <andrew@ei-grad.ru>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Conntrack logger.
"""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'tas.settings'

import sys
import logging
import traceback

from time import time, sleep
from Conntrack import EventListener, NFCT_T_DESTROY, NFCT_O_PLAIN, parse_plaintext_event

from django.db import reset_queries, transaction
from netstat.models import Session, Record


class ConntrackLogger(object):
    """
    ConntrackLogger
    """

    def __init__(self, interval=1, rawfile=None):
        """
        Create new ConntrackLogger object.

        @param interval:
            interval in seconds to syncronize data with database
        @param rawfile:
            file object to put raw statistics
        """

        #super(ConntrackLogger, self).__init__()

        self.rawfile = rawfile
        self.interval = int(interval)

        self.listener = EventListener(self.event_callback,
                NFCT_T_DESTROY, NFCT_O_PLAIN)
        self.listener.start()
        self._running = False

        self.events = []

        logging.debug('Conntrack logger initialized! interval=%d' % interval)

    def run(self):
        self._running = True
        self.loop()

    def loop(self):
        """
        Main loop.
        """

        logging.debug('Main loop started!')

        try:
            while self._running or self.events:

                t0 = time()

                events = self.events
                self.events = []

                if events:
                    t1 = time()
                    logging.info('processing %d events...' % len(events))
                    with transaction.commit_on_success():
                        if events:
                            for event in events:
                                self.handle_event(event)
                    reset_queries()
                    logging.info('processed %d events in %.1f seconds' % (len(events), time() - t1))

                if self._running and t0 < time():
                    sleep(self.interval - time() % self.interval)
        except:
            traceback.print_exc()
            self.stop()

    def raw_stat(self, *args):
        if not self.rawfile is None:
            self.rawfile.write(":".join(*args)+"\n")

    def handle_event(self, event):

        proto, d_in, d_out = parse_plaintext_event(event)

        fields = set(('src', 'dst', 'bytes'))

        if not (fields.issubset(d_in) and fields.issubset(d_out)):
            logging.warning('incomplete event: "%s"' % event)
            return

        self.raw_stat(int(time()), proto, d_in['src'], d_in.get('sport', '0'),
                d_in['dst'], d_in.get('dport', 0), d_in['bytes'], d_out['bytes'])

        handled = False

        session = self.get_session(d_in['src'])
        if not session is None:
            handled = True
            self.update_session(session, d_in, d_out)

        session = self.get_session(d_out['src'])
        if not session is None:
            handled = True
            self.update_session(session, d_out, d_in)

        if handled is False:
            logging.warning('unhandled connection: "%s"' % event)

    def get_session(self, src):
        try:
            return Session.objects.get(src=src, dt_finish=None)
        except Session.DoesNotExist:
            return None

    def get_record(self, session, dst):
        return Record.objects.get_or_create(session=session, dst=dst)[0]

    def update_session(self, session, d_in, d_out):
        logging.debug('updating %s -> %s: %s %s' % (d_in['src'], d_in['dst'], d_in['bytes'], d_out['bytes']))
        rec = self.get_record(session, d_in['dst'])
        rec.traf_in += int(d_in['bytes'])
        rec.traf_out += int(d_out['bytes'])
        rec.save()

    def stop(self):
        """
        Stop main loop.
        """

        self.listener.stop()
        self._running = False

    def event_callback(self, event):
        """
        Callback for Netfilter netlink interface.
        """

        self.events.append(event)

if __name__ == "__main__":

    # Parse command line options
    from optparse import OptionParser

    usage = 'Usage: %prog [options]'

    parser = OptionParser(usage=usage, version='0.1.1')

    parser.add_option('-d', '--debug', action='store_true', dest='debug',
            help='print debug messages',
            default=False)
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
            help='print info messages',
            default=False)
    parser.add_option('-w', '--rawfile', dest='rawfile', metavar="FILENAME",
            help='write raw statistics to file',
            default=None)
    parser.add_option('-i', '--interval', dest='interval', metavar='SECONDS',
            help='interval in seconds to syncronize data with database',
            default=1)

    opt, args = parser.parse_args()

    if opt.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    elif opt.verbose:
        logging.basicConfig(level=logging.INFO, format="%(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(message)s")

    if opt.rawfile is None:
        rawfile = None
    else:
        rawfile = open(opt.rawfile, 'a')

    # Initialize ContrackLogger
    c = ConntrackLogger(rawfile=rawfile, interval=int(opt.interval))

    # Make handler for SIGINT
    def sigint_handler(signum, frame):
        c.stop()

    import signal
    signal.signal(signal.SIGINT, sigint_handler)

    # Run ConntrackLogger loop
    c.run()

