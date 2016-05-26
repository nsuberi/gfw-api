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
import copy
import json

from appengine_config import runtime_config
from google.appengine.ext import ndb
from google.appengine.api import users
from google.appengine.api import taskqueue

from gfw.user.gfw_user import GFWUser
from gfw.models.topic import Topic
from gfw.mailers.subscription_confirmation import SubscriptionConfirmationMailer

class Subscription(ndb.Model):
    name      = ndb.StringProperty()
    topic     = ndb.StringProperty()
    email     = ndb.StringProperty()
    url       = ndb.StringProperty()
    user_id   = ndb.KeyProperty()
    pa        = ndb.StringProperty()
    use       = ndb.StringProperty()
    useid     = ndb.IntegerProperty()
    iso       = ndb.StringProperty()
    id1       = ndb.StringProperty()
    ifl       = ndb.StringProperty()
    fl_id1    = ndb.StringProperty()
    wdpaid    = ndb.IntegerProperty()
    has_geom  = ndb.BooleanProperty(default=False)
    confirmed = ndb.BooleanProperty(default=False)
    geom      = ndb.JsonProperty()
    params    = ndb.JsonProperty()
    updates   = ndb.JsonProperty()
    created   = ndb.DateTimeProperty(auto_now_add=True)
    new       = ndb.BooleanProperty(default=True)
    geostore  = ndb.StringProperty()
    overview_image = ndb.BlobProperty()

    kind = 'Subscription'

    @classmethod
    def create(cls, params, user=None):
        """Create subscription if email and, iso or geom is present"""

        subscription = Subscription()
        subscription.populate(**params)
        subscription.params = params
        subscription.has_geom = bool(params.get('geom'))

        user_id = user.key if user is not None else ndb.Key('User', None)
        subscription.user_id = user_id

        subscription.put()
        return subscription

    @classmethod
    def subscribe(cls, params, user):
        subscription = Subscription.create(params, user)
        if subscription:
            subscription.send_confirmation_email()
            return subscription
        else:
            return False

    @classmethod
    def confirm_by_id(cls, id):
        subscription = cls.get_by_id(int(id))
        if subscription:
            return subscription.confirm()
        else:
            return False

    def send_confirmation_email(self):
        taskqueue.add(url='/v2/subscriptions/tasks/confirmation',
            queue_name='pubsub-confirmation',
            params=dict(subscription=self.key.urlsafe()))

    def to_dict(self):
        result = super(Subscription,self).to_dict()
        result['key'] = self.key.id()
        return result

    def formatted_name(self):
        if (not self.name) or (len(self.name) == 0):
            return "Unnamed Subscription"
        else:
            return self.name

    def confirm(self):
        self.confirmed = True
        return self.put()

    def unconfirm(self):
        self.confirmed = False
        self.send_confirmation_email()

        return self.put()

    def unsubscribe(self):
        return self.key.delete()

    def run_analysis(self, begin, end):
        params = copy.copy(self.params)
        params['begin'] = begin
        params['end'] = end

        if 'geom' in params:
            geom = params['geom']
            if 'geometry' in geom:
                geom = geom['geometry']
            params['geojson'] = json.dumps(geom)

        topic = Topic.get_by_id(self.topic)
        return topic.execute(params)
