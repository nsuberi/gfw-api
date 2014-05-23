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
import time
import logging
import itertools
import json

HOST = 'http://localhost:8080'


def _timeit(url, params):
    start = time.clock()
    r = requests.get(url, params=params)
    ms = (time.clock() - start) * 1000
    return r, ms


class FormaTest(unittest.TestCase):

    def check(self, url, params, props, retry_count=0):
        logging.warning('%s - %s' % (url, params.keys()))
        r, ms = _timeit(url, params)
        if r.status_code == 500:
            logging.warning('RETRY=%s, ERROR=%s' % (retry_count, r.text[-99:]))
            if retry_count < 3:
                self.check(url, params, props, retry_count + 1)
        else:
            self.assertEqual(r.status_code, 200)
            result = r.json()
            [self.assertIn(x, result) for x in props]

    def setUp(self):
        self.url = '%s/forest-change/forma-alerts' % HOST
        self.world_params = [
            {},
            {'bust': 1},
            {'period': '2005-01-01,2014-01-01'},
            {'geojson': json.dumps({
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            -67.8515625,
                            -11.178401873711785
                        ],
                        [
                            -70.3125,
                            -28.30438068296277
                        ],
                        [
                            -54.84375,
                            -38.27268853598096
                        ],
                        [
                            -46.40625,
                            -14.944784875088372
                        ],
                        [
                            -67.8515625,
                            -11.178401873711785
                        ]
                    ]
                ]
                })}
        ]

    def test_world(self):
        logging.warning(self.world_params)
        combos = [x for x in itertools.combinations(self.world_params, 2)]
        params = combos + [self.world_params] + [{}]
        for param_combo in params:
            query = {}
            map(query.update, param_combo)
            self.check(self.url, query, ['value'])

if __name__ == '__main__':
    unittest.main(exit=False)
