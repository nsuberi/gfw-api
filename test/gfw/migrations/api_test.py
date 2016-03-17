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

from test import common

import mock
import unittest
import webapp2
import webtest

from gfw.v2.migrations.api import handlers

class SubscribeMigrationTest(common.BaseTest):
    def setUp(self):
        super(SubscribeMigrationTest, self).setUp()
        self.api = webtest.TestApp(handlers)

    def testRedirectIfNotLoggedIn(self):
        url = '/v2/migrations/agxkZXZ-Z2Z3LWFwaXNyFQsSCEdlb3N0b3JlGICAgICAhtsLDA/migrate'
        response = self.api.get(url, expect_errors=True)
        self.assertEqual(response.status_int, 302)
