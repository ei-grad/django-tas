#!/usr/bin/env python
# coding: utf-8
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
Utils to control Sessions.

Commands:

    split - split sessions

"""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'tas.settings'

import sys
import logging
import traceback

from time import time, sleep
from datetime import datetime

from django.db import reset_queries, transaction
from netstat.models import Session, Record


def apply_policy(session):
    raise NotImplemented()

def remove_policy(session):
    raise NotImplemented()

def start_session(user, src):
    raise NotImplemented()

def finish_session(session):
    raise NotImplemented()

def split_sessions():
    now = datetime.now()
    with transaction.commit_on_success():
        for session in Session.objects.filter(dt_finish=None):
            session.dt_finish = now
            session.save()
            new_session = Session(user=session.user, src=session.src)
            new_session.save()

if __name__ == "__main__":

    from optparse import OptionParser

    usage = 'Usage: %prog [options] cmd'

    parser = OptionParser(usage=usage, version='0.1.1')

    parser.add_option('-d', '--debug', action='store_true', dest='debug',
           help='print debug messages',
           default=False)

    opt, args = parser.parse_args()

    if opt.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    else:
        logging.basicConfig(level=logging.WARNING, format="%(message)s")

    commands = {
            'split': split_sessions
    }

    if len(args) == 0:
        logging.error(usage + __doc__)
        sys.exit(1)

    if args[0] in commands:
        commands[args[0]](*args[1:])
    else:
        logging.error('No such command!\n\n' + __doc__)

