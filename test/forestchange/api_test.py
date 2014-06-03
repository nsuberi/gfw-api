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

from gfw.forestchange import api, args
from gfw import common


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_urlfetch_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

        BASE = r'/forest-change/forma-alerts'
        app = webapp2.WSGIApplication([
            (BASE + r'/wdpa/\d+', api.FormaWdpaHandler),
            (BASE + r'/admin/[A-z]{3,3}/\d+', api.FormaIsoId1Handler),
            (BASE + r'/admin/[A-z]{3,3}', api.FormaIsoHandler),
            (BASE + r'/use/[A-z]+/\d+', api.FormaUseHandler),
            (BASE, api.FormaAllHandler),
            ])

        self.testapp = webtest.TestApp(app)

    def tearDown(self):
        self.testbed.deactivate()


class FormaTest(BaseTest):

    def test_all(self):
        path = r'/forest-change/forma-alerts'
        print '\n%s...' % path
        response = self.testapp.get(path, dict())
        self.assertIn('value', response.json)
        self.assertEqual(200, response.status_code)

    def test_iso(self):
        path = r'/forest-change/forma-alerts/admin/bra'
        print '\n%s...' % path
        response = self.testapp.get(path, dict(bust=1))
        self.assertIn('iso', response.json)
        self.assertIn('value', response.json)
        self.assertEqual(200, response.status_code)

    def test_id1(self):
        path = r'/forest-change/forma-alerts/admin/bra/1'
        print '\n%s...' % path
        response = self.testapp.get(path, dict(bust=1))
        self.assertIn('iso', response.json)
        self.assertEqual('bra', response.json['iso'])
        self.assertIn('id1', response.json)
        self.assertEqual('1', response.json['id1'])
        self.assertIn('value', response.json)
        self.assertEqual(200, response.status_code)

    def test_wdpa(self):
        path = r'/forest-change/forma-alerts/wdpa/390'
        print '\n%s...' % path
        response = self.testapp.get(path, dict(bust=1))
        self.assertIn('wdpaid', response.json)
        self.assertEqual('390', response.json['wdpaid'])
        self.assertIn('value', response.json)
        self.assertEqual(200, response.status_code)

    def test_use(self):
        path = r'/forest-change/forma-alerts/use/logging/1'
        print '\n%s...' % path
        response = self.testapp.get(path, dict(bust=1))
        self.assertIn('useid', response.json)
        self.assertEqual('1', response.json['useid'])
        self.assertIn('use', response.json)
        self.assertEqual('logging', response.json['use'])
        self.assertIn('value', response.json)
        self.assertEqual(200, response.status_code)

if __name__ == '__main__':
    reload(common)
    reload(api)
    reload(args)
    unittest.main(exit=False)
