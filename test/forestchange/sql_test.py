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

"""Unit test coverage for the gfw.forestchange.sql module.

These tests take the SQL generated from the sql module, hit the
CartoDB SQL API with it, and check the response for any errors.
"""

import unittest

from test.forestchange.common import BaseTest

import json
import urllib
import requests

from contextlib import closing

from gfw.forestchange import sql


def fetch(query):
    params = urllib.urlencode(dict(q=query))
    url = 'http://wri-01.cartodb.com/api/v2/sql?%s' % params
    with closing(requests.get(url, stream=True)) as r:
        return r


class SqlTest(BaseTest):

    def test_get_query_type(self):
        f = sql.FormaSql.get_query_type
        args = dict(format='csv')
        query_type, params = f({}, args)
        self.assertEqual('download', query_type)
        self.assertNotIn('the_geom', params)

        args = dict(format='shp')
        query_type, params = f({}, args)
        self.assertEqual('download', query_type)
        self.assertIn('the_geom', params)
        self.assertEqual(', the_geom', params['the_geom'])

        args = dict()
        query_type, params = f({}, args)
        self.assertEqual('analysis', query_type)
        self.assertNotIn('the_geom', params)

    def test_classify_query(self):
        f = sql.FormaSql.classify_query
        self.assertEqual('iso', f(dict(iso='')))
        self.assertEqual('id1', f(dict(iso='', id1='')))
        self.assertEqual('use', f(dict(use='')))
        self.assertEqual('pa', f(dict(pa='')))
        self.assertEqual('world', f(dict()))

if __name__ == '__main__':
    unittest.main(exit=False)
