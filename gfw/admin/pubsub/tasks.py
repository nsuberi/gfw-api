# Global Forest Watch API
# Copyright (C) 2015 World Resource Institute
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

import webapp2

from gfw.middlewares.cors import CORSRequestHandler
from gfw.mailers.subscription import SubscriptionMailer
from gfw.models.event import Event
from gfw.models.subscription import Subscription

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

class PubSubTaskApi(CORSRequestHandler):
    def publish_subscriptions(self):
        event = ndb.Key(urlsafe=self.args().get('event')).get()
        subscriptions = Subscription.query(Subscription.topic ==
                event.topic, Subscription.confirmed == True)

        for subscription in subscriptions.iter():
            mailer = SubscriptionMailer(subscription)
            mailer.send_for_event(event)
