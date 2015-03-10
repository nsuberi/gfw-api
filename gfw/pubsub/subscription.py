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

from appengine_config import runtime_config
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import logging
import re
from google.appengine.api import users


#
# Model
#
class Subscription(ndb.Model):
    topic = ndb.StringProperty()
    email = ndb.StringProperty()
    params = ndb.JsonProperty()
    confirmed = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

    #
    #   Class Methods
    #
    @classmethod
    def get_by_topic(cls, topic):
        """Return all confirmed Subscription entities for supplied topic."""
        return cls.query(cls.topic == topic, cls.confirmed == True).iter()

    @classmethod
    def get_by_email(cls, email):
        return cls.query(cls.email == email).iter()

    @classmethod
    def get_by_token(cls, token):
        return ndb.Key(urlsafe=token).get()

    @classmethod
    def unsubscribe(cls, topic, email):
        x = cls.query(cls.topic == topic, cls.email == email).get()
        if x:
            x.key.delete()
    
    @classmethod
    def subscribe(cls, topic, email):
        subscription = Subscription(topic=topic, email=email, params=params)
        token = subscription.put()
        if token:
            subscription.send_mail(token)

    @classmethod
    def confirm(cls,token):
        try:
            subscription = cls.get_by_token(token)
            if not subscription or subscription.confirmed:
                return False
            else:
                s.confirmed = True
                return s.put()
        except:
            return False


    #
    #   Instance Methods
    #            
    def send_mail(self,token):  
        reply_to = 'sub+%s@gfw-apis.appspotmail.com' % token.urlsafe()
        conf_url = '%s/pubsub/confirm?token=%s' % (runtime_config['APP_BASE_URL'], token.urlsafe())
        mail.send_mail(
            sender=reply_to,
            to=email,
            reply_to=reply_to,
            subject=gfw_subscribe.subject,
            body=gfw_subscribe.body % conf_url
        )






