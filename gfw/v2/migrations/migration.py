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

from appengine_config import runtime_config
from google.appengine.ext import ndb

from gfw.pubsub.subscription import Subscription
from gfw.pubsub.lib import gfw_map_url

ALLOWED_TOPICS = [
    'alerts/forma', 'alerts/terra', 'alerts/sad', 'alerts/quicc',
    'alerts/treeloss', 'alerts/prodes', 'alerts/guyra',
    'alerts/landsat', 'alerts/glad'
]

class Migration(ndb.Model):
    subscriptions = ndb.KeyProperty(repeated=True)
    email = ndb.StringProperty()

    kind = 'Migration'

    def update_subscriptions(self, user):
        for i, subscription_key in enumerate(self.subscriptions):
            subscription = subscription_key.get()
            subscription.user_id = user.key
            subscription.confirmed = True

            subscription.params = subscription.params or {}
            subscription.params['tab'] = 'analysis-tab'
            subscription.url = runtime_config.get('GFW_BASE_URL') + \
                gfw_map_url(subscription.params)

            if subscription.topic not in ALLOWED_TOPICS:
                subscription.topic = 'alerts/treeloss'

            subscription.put()
