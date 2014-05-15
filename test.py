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

"""This module provides API testing."""


import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

import argparse
import requests
import time
from uritemplate import expand


def _timeit(url, params):
    start = time.clock()
    r = requests.get(url, params=params)
    ms = (time.clock() - start) * 1000
    return r, ms


def _run_forma_tests(args):
    base = '%s/forest-change/forma-alerts' % args.host
    tests = [
        {
            'name': 'forma global',
            'url': base,
            'params': {'bust': 1},
            'status': 200,
            'props': ['value']
        },
        {
            'name': 'forma global + period',
            'url': base,
            'params': {'bust': 1, 'period': '2006-01-01,2012-01-01'},
            'status': 200,
            'props': ['value', 'begin', 'end']
        },
        {
            'name': 'forma global + use logging',
            'url': base,
            'params': {'bust': 1, 'use': 'logging,1'},
            'status': 200,
            'props': ['value', 'use', 'use_pid']
        },
        {
            'name': 'forma global + use oilpalm',
            'url': base,
            'params': {'bust': 1, 'use': 'oilpalm,1'},
            'status': 200,
            'props': ['value', 'use', 'use_pid']
        },
        {
            'name': 'forma global + use mining',
            'url': base,
            'params': {'bust': 1, 'use': 'mining,1'},
            'status': 200,
            'props': ['value', 'use', 'use_pid']
        },
        {
            'name': 'forma global + use fiber',
            'url': base,
            'params': {'bust': 1, 'use': 'fiber,1'},
            'status': 200,
            'props': ['value', 'use', 'use_pid']
        },
        {
            'name': 'forma iso',
            'url': '%s/bra' % base,
            'params': {'bust': 1},
            'status': 200,
            'props': ['value', 'iso']
        },
        {
            'name': 'forma iso with period',
            'url': '%s/bra' % base,
            'params': {'bust': 1, 'period': '2010-01-01,2013-01-01'},
            'status': 200,
            'props': ['value', 'iso']
        },
        {
            'name': 'forma iso/id1',
            'url': '%s/bra/1' % base,
            'params': {'bust': 1},
            'status': 200,
            'props': ['value', 'iso', 'id1']
        },
        {
            'name': 'forma iso/id1 with period',
            'url': '%s/bra/1' % base,
            'params': {'bust': 1, 'period': '2010-01-01,2013-01-01'},
            'status': 200,
            'props': ['value', 'iso', 'id1']
        },
        {
            'name': 'forma iso/id1 with download csv',
            'url': '%s/bra/1' % base,
            'params': {'bust': 1, 'download': 'forma_bra_1.csv'},
            'status': 200,
            'props': [],
            'headers': {
                'Content-Type': lambda x: 'text/csv' in x,
                'Content-Disposition': lambda x: 'attachment' in x
            }
        },
        {
            'name': 'forma iso/id1 with download kml',
            'url': '%s/bra/1' % base,
            'params': {'bust': 1, 'download': 'forma_bra_1.kml'},
            'status': 200,
            'props': [],
            'headers': {
                'Content-Type': lambda x: 'application/kml' in x,
                'Content-Disposition': lambda x: 'attachment' in x
            }
        },
        {
            'name': 'forma iso/id1 with download geojson',
            'url': '%s/bra/1' % base,
            'params': {'bust': 1, 'download': 'forma_bra_1.geojson'},
            'status': 200,
            'props': [],
            'headers': {
                'Content-Type': lambda x: 'application/json' in x,
                'Content-Disposition': lambda x: 'attachment' in x
            }
        },
        {
            'name': 'forma iso/id1 with download svg',
            'url': '%s/bra/1' % base,
            'params': {'bust': 1, 'download': 'forma_bra_1.svg'},
            'status': 200,
            'props': [],
            'headers': {
                'Content-Type': lambda x: 'image/svg+xml' in x,
                'Content-Disposition': lambda x: 'attachment' in x
            }
        },
        {
            'name': 'forma iso/id1 with download shp',
            'url': '%s/bra/1' % base,
            'params': {'bust': 1, 'download': 'forma_bra_1.shp'},
            'status': 200,
            'props': [],
            'headers': {
                'Content-Type': lambda x: 'application/zip' in x,
                'Content-Disposition': lambda x: 'attachment' in x
            }
        }
    ]

    for test in tests:
        print '%s - %s %s' % (test['name'], test['url'], test['params'])
        r, ms = _timeit(test['url'], test['params'])
        assert r.status_code == test['status'], r.text
        if not 'download' in test['params']:
            try:
                response = r.json()
                for prop in test['props']:
                    assert prop in response, 'missing %s' % prop
            except:
                print r.text, r.headers
                raise
        if 'headers' in test:
            for name, f in test['headers'].iteritems():
                assert f(r.headers[name]), 'wrong header value for %s' % name
        print r, ms


def _forest_change(args):
    if 'forma' in args.target:
        _run_forma_tests(args)


def _get_args():
    """Return command line arguments."""
    parser = argparse.ArgumentParser(description='GFW API test suite')
    parser.add_argument('--host', dest='host', default='http://localhost:8080',
                        help='host for the API (e.g., http://localhost:8080)')
    parser.add_argument('--target', dest='target', default='all',
                        help='test target  (e.g., forest-change/forma)')
    return parser.parse_args()


if __name__ == '__main__':
    args = _get_args()
    if 'forest-change' in args.target:
        _forest_change(args)
