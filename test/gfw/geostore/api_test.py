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

"""Unit tests for gfw.geostore"""

from test import common

import unittest
import webapp2
import webtest
import json

from gfw.geostore.api import GeostoreHandler
from gfw.geostore.api import handlers

from gfw.geostore.geostore import Geostore

class GeostoreTest(common.BaseTest):
    def setUp(self):
        super(GeostoreTest, self).setUp()
        self.api = webtest.TestApp(handlers)

    def testPost(self):
        geojson = """{
                      "type":"Polygon",
                      "coordinates":[
                        [
                          [
                            -58.97460937499999,
                            -4.12728532324537
                          ],
                          [
                            -60.732421875,
                            -7.798078531355291
                          ],
                          [
                            -55.634765625,
                            -7.972197714386866
                          ],
                          [
                            -54.84375,
                            -4.653079918274038
                          ],
                          [
                            -58.97460937499999,
                            -4.12728532324537
                          ]
                        ]
                      ]
                    }"""
        params = json.dumps({'geojson': geojson})
        response = self.api.post('/geostore', params)

        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.content_type, 'application/json')

if __name__ == '__main__':
    unittest.main(exit=False, failfast=True)
