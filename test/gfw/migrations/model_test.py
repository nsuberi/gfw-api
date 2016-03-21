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

"""Unit tests for gfw.pubsub"""

from test import common

import unittest
import webapp2
import webtest

from gfw.user.gfw_user import GFWUser
from gfw.pubsub.subscription import Subscription
from gfw.v2.migrations.migration import Migration

class MigrationTest(common.BaseTest):
    def testModelExists(self):
        self.assertIsNotNone(Migration)

    def testUpdateSubscriptions(self):
        subscription = Subscription()
        subscription.put()

        migration = Migration()
        migration.subscriptions = [subscription.key]
        migration.put()

        user = GFWUser()
        user.auth_ids = ['123']
        user.put()

        migration.update_subscriptions(user)

        self.assertIsNotNone(subscription.key.get().user_id)
        self.assertEqual(subscription.key.get().user_id.urlsafe(),
            user.key.urlsafe())

    def testCreateMigrations(self):
        user = GFWUser()
        user.auth_ids = ['123']
        user.put()
        new_subscription = Subscription()
        new_subscription.user_id = user.key
        new_subscription.put()

        subscription = Subscription()
        subscription.params = {'iso': 'ALB'}
        subscription.email = 'an@email.com'
        subscription.put()

        Migration.create_from_subscriptions()

        migration_count = Migration.query().count()
        self.assertEqual(migration_count, 1)

        migration = Migration.query().fetch()[0]
        self.assertEqual(migration.email, 'an@email.com')
        self.assertEqual(len(migration.subscriptions), 1)
        self.assertEqual(migration.subscriptions[0], subscription.key)
