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

IGNORED_TOPICS = [
    'updates/forma'
]

class Migration(ndb.Model):
    subscriptions = ndb.KeyProperty(repeated=True)
    email = ndb.StringProperty()
    complete = ndb.BooleanProperty(default=False)

    kind = 'Migration'

    @classmethod
    def create_for_email(cls, email):
        migration = cls.query(cls.email == email).fetch()
        if len(migration) > 0:
            migration = migration[0]
        else:
            migration = cls()
            migration.email = email

        if migration.complete == True:
            return

        subscriptions = Subscription.query(Subscription.email == email)
        for subscription in subscriptions.iter():
            if hasattr(subscription, 'user_id') and subscription.user_id != None: continue
            migration.subscriptions.append(subscription.key)

        if len(migration.subscriptions) > 0:
            migration.complete = True
            migration.put()

        return migration

    @classmethod
    def create_from_subscriptions(cls):
        query_set = Subscription.query(projection=["email"], distinct=True)
        unique_emails = [data.email for data in query_set]

        for email in unique_emails:
            cls.create_for_email(email)

    def update_subscriptions(self, user):
        for i, subscription_key in enumerate(self.subscriptions):
            subscription = subscription_key.get()

            if subscription.topic in IGNORED_TOPICS:
                continue

            subscription.user_id = user.key
            subscription.confirmed = True

            if subscription.topic not in ALLOWED_TOPICS:
                subscription.topic = 'alerts/treeloss'
                subscription.params['topic'] = 'alerts/treeloss'

            subscription.params = subscription.params or {}
            subscription.params['tab'] = 'analysis-tab'
            subscription.url = runtime_config.get('GFW_BASE_URL') + \
                gfw_map_url(subscription.params)

            subscription.put()
