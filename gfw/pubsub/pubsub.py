# Global Forest Watch API
# Copyright (C) 2013 World Resource Institute
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""This module supports pubsub."""

import json
import webapp2
import monitor
import datetime

from gfw import polyline
from gfw import forma
from gfw import cdb

from gfw.mailers import gfw_subscribe
from gfw.notifiers.gfw_notify import GFWNotify

from appengine_config import runtime_config
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import logging
import re
from google.appengine.api import users

#
# Handlers
#
class Subscriber(InboundMailHandler):
    def receive(self, message):
        if message.to.find('<') > -1:
            urlsafe = message.to.split('<')[1].split('+')[1].split('@')[0]
        else:
            urlsafe = message.to.split('+')[1].split('@')[0]
        s = ndb.Key(urlsafe=urlsafe).get()
        s.confirmed = True
        s.put()


class Confirmer(webapp2.RequestHandler):
    def get(self):
        urlsafe = self.request.get('token')
        if not urlsafe:
            self.error(404)
            return
        try:
            s = ndb.Key(urlsafe=urlsafe).get()
        except:
            self.error(404)
            return
        if not s:
            self.error(404)
            return
        if s.confirmed:
            self.error(404)
            return
        else:
            s.confirmed = True
            s.put()
        self.response.write('Subscription confirmed!')


class Publisher(webapp2.RequestHandler):
    def post(self):
        """Publish notifications to all event subscribers."""
        e = ndb.Key(urlsafe=self.request.get('event')).get()

        if not e.multicasted:
            for s in Subscription.get_by_topic(e.topic):
                n = Notification.get(e, s)
                if not n:
                    n = Notification.create(e, s)
                    n.put()

                taskqueue.add(
                    url='/pubsub/notify',
                    queue_name='pubsub-notify',
                    params=dict(notification=n.key.urlsafe()))
        e.multicasted = True
        e.put()


class SubscriptionDump(webapp2.RequestHandler):
    def get(self):
        email = self.request.get('email')
        subs = [x.to_dict(exclude=['created']) for x in Subscription.get_by_email(email)]
        self.response.headers.add_header('charset', 'utf-8')
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(json.dumps(subs, sort_keys=True))





