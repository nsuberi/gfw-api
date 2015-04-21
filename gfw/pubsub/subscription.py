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

from gfw.mailers import subscribe_mailer

from appengine_config import runtime_config
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
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
    def get_confirmed(cls):
        """Return all confirmed Subscription entities"""
        return cls.query(cls.confirmed == True).iter()

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
    def subscribe(cls, topic, email, params):        
        subscription = Subscription(topic=topic, email=email, params=params)
        token = subscription.put()
        if token:           
            subscription.send_mail(token,email)
            return True
        else:
            return False

    @classmethod
    def confirm(cls,token):
        subscription = cls.get_by_token(token)
        try:
            if not subscription or subscription.confirmed:
                return False
            else:
                subscription.confirmed = True
                return subscription.put()
        except:
            return False


    #
    #   Instance Methods
    #            
    def send_mail(self,token,email):  
        reply_to = 'sub+%s@gfw-apis.appspotmail.com' % token.urlsafe()
        conf_url = '%s/pubsub/confirm?token=%s' % (runtime_config['APP_BASE_URL'], token.urlsafe())
        mail.send_mail(
            sender=reply_to,
            to=email,
            reply_to=reply_to,
            subject=subscribe_mailer.subject,
            body=subscribe_mailer.body % conf_url
        )






