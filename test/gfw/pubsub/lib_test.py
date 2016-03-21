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

from gfw.pubsub.lib import gfw_map_url

class PubSubLibTest(common.BaseTest):
    def testNoParams(self):
        self.assertEqual(gfw_map_url(None), '/map')
        self.assertEqual(gfw_map_url({}), '/map')

    def testItIgnoresLongGeojson(self):
        params = {
            'geom': { "type": "FeatureCollection", "features": [ { "type": "Feature", "properties": {}, "geometry": { "type": "Polygon", "coordinates": [ [ [ 25.3125, 58.44773280389084 ], [ 19.6875, 60.58696734225869 ], [ 19.6875, 56.9449741808516 ], [ 11.953125, 58.81374171570782 ], [ 11.953125, 56.36525013685606 ], [ 3.8671874999999996, 56.36525013685606 ], [ 4.5703125, 52.908902047770255 ], [ -1.7578125, 52.05249047600099 ], [ 2.8125, 50.064191736659104 ], [ -0.3515625, 44.33956524809713 ], [ 5.9765625, 45.583289756006316 ], [ 5.9765625, 40.44694705960048 ], [ 8.0859375, 41.244772343082076 ], [ 11.953125, 35.746512259918504 ], [ 14.414062499999998, 39.36827914916011 ], [ 23.90625, 31.05293398570514 ], [ 23.90625, 38.272688535980976 ], [ 33.75, 35.17380831799959 ], [ 31.9921875, 37.996162679728116 ], [ 39.375, 37.996162679728116 ], [ 35.15625, 41.77131167976407 ], [ 46.7578125, 42.81152174509788 ], [ 40.078125, 44.59046718130883 ], [ 45.3515625, 46.31658418182218 ], [ 38.67187499999999, 49.15296965617042 ], [ 46.05468749999999, 51.6180165487737 ], [ 39.0234375, 52.482780222078226 ], [ 41.1328125, 55.97379820507658 ], [ 36.2109375, 55.57834467218206 ], [ 36.2109375, 60.23981116999893 ], [ 33.046875, 58.07787626787517 ], [ 25.3125, 58.44773280389084 ] ] ] } } ] }
        }

        self.assertEqual(gfw_map_url(params),
            '/map/-1/0/0/ALL/grayscale/loss?')

    def testGfwUrl(self):
        params = {
            'tab': 'analysis-tab',
            'topic': 'alerts/glad',
            'iso': 'ALB',
            'id1': 1,
            'geom': {'type': 'FeatureCollection'}
        }

        self.assertEqual(gfw_map_url(params),
            '/map/-1/0/0/ALB-1/grayscale/umd_as_it_happens?geojson=%7B%22type%22%3A+%22FeatureCollection%22%7D&tab=analysis-tab')
