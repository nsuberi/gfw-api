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

"""Unit test coverage for the gfw.countries module."""

from test import common

import unittest
import webapp2
import webtest

from gfw.countries import api
from gfw.countries import countries


class CountriesTest(common.BaseTest):

    def testExecute(self):
        action, data = countries.execute(dict(iso='bra'))
        self.assertEqual(action, 'respond')
        self.assertNotEqual(data, None)
        for key in ['topojson', 'bounds', 'subnat_bounds', 'forma', 'tenure',
                    'umd']:
            self.assertIn(key, data)
            self.assertNotEqual(data[key], None)


class CountriesApiTest(common.BaseTest):

    def setUp(self):
        super(CountriesApiTest, self).setUp()
        app = webapp2.WSGIApplication([(r'/countries.*', api.Handler)])
        self.api = webtest.TestApp(app)
        self.args = [
            ('bust', 1),
            ('dev', 1),
            ('thresh', 10)]

    def test_classify_request(self):
        path = '/countries/foo'
        self.assertEqual('iso', api._classify_request(path))
        path = '/countries/foo/1'
        self.assertEqual('id1', api._classify_request(path))

    def testGetNational(self):
        path = r'/countries/bra'
        for combo in common.combos(self.args):
            args = dict(combo)
            for thresh in [10, 15, 20, 25, 30, 50, 75]:
                args['thresh'] = thresh
                r = self.api.get(path, args)
                data = r.json
                for year in data['umd']:
                    self.assertEqual(thresh, year['thresh'])
                self.assertIn('params', r.json)
                self.assertIn('iso', r.json['params'])
                self.assertEqual(200, r.status_code)

if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
