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
