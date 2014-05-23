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

import requests
import unittest
import logging
import itertools
import json

HOST = 'http://localhost:8080'
TEST_DOWNLOAD = False


def combos(params, repeat=None, min=None):
    result = set()
    if not repeat:
        repeat = len(params) + 1
    if not min:
        min = 1
    for x in range(min, repeat):
        result.update(itertools.combinations(params, x))
    return result


class ForestChangeTest(unittest.TestCase):

    def check_download(self, r, download):
        self.assertIn('attachment', r.headers['Content-Disposition'])
        if download.endswith('.csv'):
            self.assertIn('text/csv', r.headers['Content-Type'])
        elif download.endswith('.kml'):
            self.assertIn('application/kml', r.headers['Content-Type'])
        elif download.endswith('.geojson'):
            self.assertIn('application/json', r.headers['Content-Type'])
        elif download.endswith('.svg'):
            self.assertIn('image/svg+xml', r.headers['Content-Type'])
        elif download.endswith('.shp'):
            self.assertIn('application/zip', r.headers['Content-Type'])

    def check(self, url, params, props, retry_count=0):
        logging.warning('%s - %s' % (url, params))
        r = requests.get(url, params=params)
        if r.status_code == 500:
            logging.warning('RETRY=%s, ERROR=%s' % (retry_count, r.text[-99:]))
            if retry_count < 3:
                self.check(url, params, props, retry_count + 1)
            else:
                self.fail('Retried %s times' % retry_count)
        else:
            self.assertEqual(r.status_code, 200)
            if 'download' in params:
                self.check_download(r, params['download'])
            else:
                result = r.json()
                [self.assertIn(x, result) for x in props]


class FormaTest(ForestChangeTest):
    def setUp(self):
        self.params = [
            ('bust', 1),
            ('period', '2008-01-01,2009-01-01'),
            ('geojson', json.dumps({
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -51.50390625,
                            -11.695272733029402
                        ],
                        [
                            -51.50390625,
                            -13.154376055418515
                        ],
                        [
                            -49.21875,
                            -13.154376055418515
                        ],
                        [
                            -49.21875,
                            -11.60919340793894
                        ],
                        [
                            -51.50390625,
                            -11.695272733029402
                        ]
                    ]
                ]
                }))
        ]
        self.params_download = self.params + \
            [('download', 'forma.csv'),
             ('download', 'forma.kml'),
             ('download', 'forma.geojson'),
             ('download', 'forma.svg'),
             ('download', 'forma.shp')]


class FormaWorldTest(FormaTest):

    def setUp(self):
        super(FormaWorldTest, self).setUp()
        self.url = '%s/forest-change/forma-alerts' % HOST
        self.params += [
            ('use', 'logging,1'),
            ('use', 'mining,1'),
            ('use', 'fiber,1'),
            ('use', 'oilpalm,1')]

    def test_analysis(self):
        for combo in combos(self.params):
            self.check(self.url, dict(combo), ['value'])
        self.check(self.url, dict(), ['value'])  # No params

    def test_download(self):
        if TEST_DOWNLOAD:
            for combo in combos(self.params_dowload, min=2):
                params = dict(combo)
                if len(params) == 1:
                    continue
                if 'download' not in params:
                    continue
                self.check(self.url, params, ['value'])


class FormaIsoTest(FormaTest):

    def setUp(self):
        super(FormaIsoTest, self).setUp()
        self.url = '%s/forest-change/forma-alerts/idn' % HOST

    def test_analysis(self):
        for combo in combos(self.params):
            self.check(self.url, dict(combo), ['value'])
        self.check(self.url, dict(), ['value'])  # No params

    def test_download(self):
        if TEST_DOWNLOAD:
            for combo in combos(self.params_dowload, min=2):
                params = dict(combo)
                if len(params) == 1:
                    continue
                if 'download' not in params:
                    continue
                self.check(self.url, params, ['value'])


if __name__ == '__main__':
    unittest.main(exit=False)
