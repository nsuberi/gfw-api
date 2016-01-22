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
import logging

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
    name      = ndb.StringProperty()
    topic     = ndb.StringProperty()
    email     = ndb.StringProperty()
    url       = ndb.StringProperty()
    user_id   = ndb.KeyProperty()
    iso       = ndb.StringProperty()
    id1       = ndb.StringProperty()
    has_geom  = ndb.BooleanProperty(default=False)
    confirmed = ndb.BooleanProperty(default=False)
    geom      = ndb.JsonProperty()
    params    = ndb.JsonProperty()
    updates   = ndb.JsonProperty()
    created   = ndb.DateTimeProperty(auto_now_add=True)

    kind = 'Subscription'

    """ Class Methods """

    @classmethod
    def create(cls, params, user=None):
        """Create subscription if email and, iso or geom is present"""

        iso = params.get('iso')
        has_geom = bool(params.get('geom'))
        if iso or has_geom:
            subscription = Subscription()
            subscription.populate(**params)
            subscription.params = params
            subscription.has_geom = has_geom

            user_id = user.key if user is not None else ndb.Key('User', None)
            subscription.user_id = user_id

            subscription.put()
            return subscription
        else:
            return False

    #
    #   Query Helpers
    #

    @classmethod
    def with_token(cls, token):
        """Return subscription for a given token"""
        token_type = type(token)
        if (token_type is str) or (token_type is unicode):
            subscription = ndb.Key(urlsafe=token).get()
            if subscription.key.kind()==cls.kind:
                subscription = subscription
            else:
                subscription = False
        else:
            subscription = token.get()
        return subscription

    @classmethod
    def with_confirmation(cls):
        """Return all confirmed Subscription entities"""
        return cls.query(cls.confirmed == True).iter()

    @classmethod
    def without_confirmation(cls):
        """Return all unconfirmed Subscription entities"""
        return cls.query(cls.confirmed == True).iter()

    @classmethod
    def with_topic(cls, topic):
        """Return all confirmed Subscription entities for supplied topic."""
        return cls.query(cls.topic == topic, cls.confirmed == True).iter()

    @classmethod
    def with_email(cls, email):
        return cls.query(cls.email == email).iter()

    #
    # Subscriptions
    #


    @classmethod
    def subscribe(cls, params, user):
        subscription = Subscription.create(params, user)
        if subscription:
            subscription.send_mail()
            return subscription
        else:
            return False

    @classmethod
    def unsubscribe_by_token(cls, token):
        subscription = cls.with_token(token)
        if subscription:
            return subscription.unsubscribe()

    @classmethod
    def unsubscribe_all(cls, topic, email):
        subs = cls.query(cls.topic == topic, cls.email == email)
        for sub in subs:
            sub.unsubscribe()

    @classmethod
    def confirm_by_token(cls,token):
        subscription = cls.with_token(token)
        if subscription:
            return subscription.confirm()
        else:
            return False


    """ Instance Methods """

    def to_dict(self):
        result = super(Subscription,self).to_dict()
        result['key'] = self.key.id()
        return result
    #
    # Subscriptions
    #

    def confirm(self):
        if not self.confirmed:
            self.confirmed = True
            return self.put()

    def unsubscribe(self):
        return self.key.delete()

    #
    # Mailer
    #

    def send_mail(self):
        safe_token = self.key.urlsafe()
        reply_to = 'sub+%s@gfw-apis.appspotmail.com' % safe_token
        conf_url = '%s/pubsub/confirm?token=%s' % (runtime_config['APP_BASE_URL'], safe_token)
        logging.info("sending confirmation email: %s" % safe_token)
        mail.send_mail(
            sender=reply_to,
            to=self.email,
            reply_to=reply_to,
            subject=subscribe_mailer.subject,
            body=subscribe_mailer.body % conf_url
        )
