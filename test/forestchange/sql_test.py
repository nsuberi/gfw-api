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

"""Unit test coverage for gfw.forestchange.args"""

import json
import unittest
import urllib
import requests

from google.appengine.ext import testbed

from gfw.forestchange import sql


def fetch(query):
    params = urllib.urlencode(dict(q=query))
    url = 'http://wri-01.cartodb.com/api/v2/sql?%s' % params
    print 'Fetching query: %s...\n%s' % (query, url)
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        response = requests.get(url)
        if response.status_code == 200:
            return response
        print 'ERROR %s' % response.text
        retry_count += 1
    return response


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()


class SqlTest(BaseTest):

    def test_classify_query(self):
        f = sql.FormaSql.classify_query
        self.assertEqual('iso', f(dict(iso='')))
        self.assertEqual('id1', f(dict(iso='', id1='')))
        self.assertEqual('use', f(dict(use='')))
        self.assertEqual('pa', f(dict(pa='')))
        self.assertEqual('world_download', f(dict(format='')))
        self.assertEqual('world', f(dict()))

    def test_world(self):
        f = sql.FormaSql.process
        args = dict()
        query = f(args)
        self.assertIsNotNone(query)
        response = fetch(query)
        print response
        self.assertEqual(200, response.status_code)
        self.assertIn('rows', response.json())
        self.assertEqual(1, len(response.json()['rows']))
        self.assertIn('value', response.json()['rows'][0])

        geojson = {"type": "Polygon", "coordinates": [[
            [-58.35937499999999, -5.615985819155327],
            [-58.35937499999999, -17.97873309555617],
            [-50.2734375, -16.97274101999901],
            [-49.92187499999999, -4.565473550710278],
            [-58.35937499999999, -5.615985819155327]]]}

        # GeoJSON test
        args = dict(geojson=json.dumps(geojson))
        query = f(args)
        self.assertIsNotNone(query)
        response = fetch(query)
        print response
        self.assertEqual(200, response.status_code)
        self.assertIn('rows', response.json())
        self.assertEqual(1, len(response.json()['rows']))
        self.assertIn('value', response.json()['rows'][0])

    def test_use(self):
        f = sql.FormaSql.process
        for use in ['logging', 'mining', 'oilpalm', 'fiber']:
            args = dict(use=use, useid=1)
            query = f(args)
            self.assertIsNotNone(query)
            response = fetch(query)
            print response
            self.assertEqual(200, response.status_code)
            self.assertIn('rows', response.json())
            self.assertGreaterEqual(len(response.json()['rows']), 0)
            if response.json()['rows']:
                self.assertIn('value', response.json()['rows'][0])

    def test_id1(self):
        f = sql.FormaSql.process
        args = dict(iso='bra', id1=1)
        query = f(args)
        self.assertIsNotNone(query)
        response = fetch(query)
        print response
        self.assertEqual(200, response.status_code)
        self.assertIn('rows', response.json())
        self.assertEqual(1, len(response.json()['rows']))
        self.assertIn('value', response.json()['rows'][0])

    def test_iso(self):
        f = sql.FormaSql.process
        for iso in ['bra', 'BRA']:
            args = dict(iso=iso)
            query = f(args)
            self.assertIsNotNone(query)
            response = fetch(query)
            print response
            self.assertEqual(200, response.status_code)
            self.assertIn('rows', response.json())
            self.assertEqual(1, len(response.json()['rows']))
            self.assertIn('value', response.json()['rows'][0])

    def test_wdpa(self):
        f = sql.FormaSql.process
        args = dict(wdpaid=8950)
        query = f(args)
        self.assertIsNotNone(query)
        response = fetch(query)
        print response
        self.assertEqual(200, response.status_code)
        self.assertIn('rows', response.json())
        self.assertEqual(1, len(response.json()['rows']))
        self.assertIn('value', response.json()['rows'][0])

if __name__ == '__main__':
    reload(sql)
    unittest.main(exit=False)
