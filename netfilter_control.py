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
Firewall of Traffic Accounting System


"""

from threading import Thread
from time import sleep
import traceback

from netfilter.rule import Rule, Match
from netfilter.table import Table


class Firewall(object):

    def __init__(self):

        for user in User.objects.all():
            self.create_user_tables(user)
            
        for session in Session.objects.filter(dt_finish=None)
            username = session.user.username
            Table('filter').append_rule('FORWARD',
                    Rule(
                        source=session.src,
                        jump=username+'-access-out'
                ))
            Table('filter').append_rule('FORWARD',
                    Rule(
                        destination=session.src,
                        jump=username+'-access-in'
                ))
            Table('nat').append_rule('PREROUTING',
                    Rule(
                        source=session.src,
                        jump='ACCEPT'
                    )
            
        self.create_redirect_rules()
    
    def create_user_tables(self, user):

        if UserDepartament.objects.filter(user=user).count():
            depart = UserDepartament.objects.get(user=user).departament
            depart_quota_chain = ":".join(depart.name, "quota")
            user_quota_chain_jump = depart_quota_chain
        else:
            user_quota_chain_jump = 'RETURN'

        if UserQuotaPolicy.objects.filter(user=user).count():
            user_quota_policy = UserQuotaPolicy.objects.get(user=user)

            user_quota_chain = ":".join(user, "quota")
            
            Table('filter').create_chain(user_quota_chain)
            Table('filter').append_rule(user_quota_chain,
                Rule(
                    jump=user_quota_chain_jump,
                    matches=[Match('quota', '--quota %d' % (
                user_quota_policy.quota.full - user_quota_policy.user
                            ))],
                        ))

        # append user departament rules
        try:
            Table('filter').append_rule(user_quota_chain,
                    Rule(jump=depart_quota_chain)
                )
        except:
            Table('filter').append_rule(user_quota_chain,
                    Rule(jump='RETURN')
                )

        
        Table('filter').append_rule(user+'-access', Rule(jump=user+'-quota'))
        
        Table('filter').append_rule(user+'-quota', Rule(jump=user+'-childs', matches=[
            Match('quota', '--quota ' + str(users[user].quota_left))
        ]))
        
        for i in tree.get_childs(user):
            create_rules_for_user(i, users, tree)
            Table('filter').append_rule(user+'-childs', Rule(jump=i+'-access', matches=[
                Match('recent', '--rcheck --rsource --name ' + i)]))
            Table('filter').append_rule(user+'-childs', Rule(jump=i+'-access', matches=[
                Match('recent', '--rcheck --rdest --name ' + i)]))

def create_redirect_rules(self):
    Table('nat').append_rule('PREROUTING',
            Rule(
                in_interface=self.in_interface,
                jump='DNAT --to-destination %s:%s' % \
                        (self.redirector_ip, self.redirector_port)
        ))


#    global sync_quotas_timer
#    sync_quotas_timer = Timer(config.sync_quotas_interval,
#        sync_quotas, (users.keys(),))
#    print "sync_quotas: set"
#    sync_quotas_timer.setDaemon(True)
#
def sync_quotas(s, users):
    
    print "sync_quotas: start"
    
    for i in users:
        quota_left = int(Table('filter').list_rules(i.login+'-quota')[-1].\
            matches[0].options()['quota'][0])
        if i.quota_left != quota_left:
            print "sync_quotas: differ", i.login, i.quota_left, "->", quota_left
            i.quota_left = quota_left
            s.update(i)
    
    print "sync_quotas: finish"

