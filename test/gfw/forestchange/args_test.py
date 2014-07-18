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

from test import common

import unittest
import json

from gfw.forestchange import args


class PathProcessorTest(common.BaseTest):

    def test_process_path(self):
        path = '/forest-change/forma-alerts/admin/bra'
        value = args.process_path(path, 'iso')
        self.assertEqual({'iso': 'bra'}, value)

        path = '/forest-change/forma-alerts/admin/bra/123'
        value = args.process_path(path, 'id1')
        self.assertEqual({'iso': 'bra', 'id1': '123'}, value)

        path = '/forest-change/forma-alerts/wdpa/123'
        value = args.process_path(path, 'wdpaid')
        self.assertEqual({'wdpaid': '123'}, value)

        path = '/forest-change/forma-alerts/use/logging/123'
        value = args.process_path(path, 'use')
        self.assertEqual({'use': 'logging', 'useid': '123'}, value)


class ArgsTest(common.BaseTest):

    def test_period(self):
        f = args.ArgProcessor.period
        begin = '2000-01-01'
        end = '2014-01-01'
        for x in ['%s,%s' % (begin, end)]:
            self.assertEqual(f(x)['begin'], begin)
            self.assertEqual(f(x)['end'], end)

        with self.assertRaises(args.PeriodArgError):
            f('2000-01-02')
        with self.assertRaises(args.PeriodArgError):
            f('2000-01-02,')
        with self.assertRaises(args.PeriodArgError):
            f(',2000-01-02')
        with self.assertRaises(args.PeriodArgError):
            f('2000-1-2,1999-1-2')  # begin > end

    def test_geojson(self):
        f = args.ArgProcessor.geojson
        arg = '{"type": "Polygon"}'
        self.assertEquals(f(arg)['geojson'], arg)
        arg = '{"type": "MultiPolygon"}'
        self.assertEquals(f(arg)['geojson'], arg)
        with self.assertRaises(args.GeoJsonArgError):
            f(json.dumps({"type": "Line"}))  # Wrong type
        with self.assertRaises(args.GeoJsonArgError):
            f('{"type": Polygon}')  # Invalid JSON

    def test_download(self):
        f = args.ArgProcessor.download
        arg = 'foo.csv'
        self.assertEqual(f(arg)['format'], 'csv')
        self.assertEqual(f(arg)['filename'], 'foo')
        with self.assertRaises(args.DownloadArgError):
            f('foo')

    def test_use(self):
        f = args.ArgProcessor.use
        for arg in ['logging', 'mining', 'oilpalm', 'fiber']:
            self.assertEqual(f(arg)['use'], arg)
        with self.assertRaises(args.UseArgError):
            f('boom')

    def test_bust(self):
        f = args.ArgProcessor.bust
        self.assertTrue(f('bust')['bust'])

    def test_dev(self):
        f = args.ArgProcessor.dev
        self.assertTrue(f('dev')['dev'])

    def test_process(self):
        f = args.ArgProcessor.process
        params = {
            "period": "2007-1-1,2008-1-1",
            "bust": "",
            "dev": "",
            "use": "logging",
            "useid": "1",
            "download": "foo.csv",
            "geojson": '{"type": "Polygon"}'
        }
        x = f(params)
        self.assertItemsEqual(
            ['begin', 'end', 'use', 'useid', 'filename', 'format',
                'geojson', 'dev', 'bust'],
            x)

if __name__ == '__main__':
    unittest.main(exit=False)
