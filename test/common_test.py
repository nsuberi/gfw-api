# Global Forest Watch API
# Copyright (C) 2014 World Resource Institute
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

"""Unit test coverage for gfw.common"""

import json
import unittest
import webapp2
import webtest

from google.appengine.ext import testbed

from gfw import common


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        app = webapp2.WSGIApplication([('/', common.CORSRequestHandler)])
        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()


class CommonTest(BaseTest):

    def test_args(self):
        response = self.testapp.args('/', dict(a=1, b=2, c=3))
        print response


if __name__ == '__main__':
    reload(common)
    unittest.main(exit=False)
