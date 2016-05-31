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

from test import common

import unittest
import webapp2
import webtest
import mock

import datetime

from gfw.forestchange import glad

class GladTest(common.FetchBaseTest):
    def testRastersForPeriod(self):
        begin = datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')
        end = datetime.datetime.strptime('2015-02-01', '%Y-%m-%d')
        rasters = glad.rastersForPeriod(begin, end)
        self.assertEqual([1], rasters)

        begin = datetime.datetime.strptime('2016-01-01', '%Y-%m-%d')
        end = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
        rasters = glad.rastersForPeriod(begin, end)
        self.assertEqual([2], rasters)

        begin = datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')
        end = datetime.datetime.strptime('2016-02-01', '%Y-%m-%d')
        rasters = glad.rastersForPeriod(begin, end)
        self.assertEqual([1, 2], rasters)

    def testDateToGridCode(self):
        date = datetime.datetime.strptime('2015-01-01', '%Y-%m-%d')
        grid_code = glad.dateToGridCode(date)
        self.assertEqual(1, grid_code)

        date = datetime.datetime.strptime('2015-07-04', '%Y-%m-%d')
        grid_code = glad.dateToGridCode(date)
        self.assertEqual(185, grid_code)

        date = datetime.datetime.strptime('2016-01-01', '%Y-%m-%d')
        grid_code = glad.dateToGridCode(date)
        self.assertEqual(366, grid_code)

    def testGeojsonToEsriJson(self):
        geojson = '{ "coordinates": [[123, 123],[123,123]] }'
        expectedEsriJson = {
            "rings": [[123, 123],[123,123]],
            "spatialReference": { 'wkid': 4326 }
        }

        self.assertEqual(expectedEsriJson, glad.geojsonToEsriJson(geojson))


if __name__ == '__main__':
    unittest.main(exit=False, failfast=True)
