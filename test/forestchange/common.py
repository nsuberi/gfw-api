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

"""Unit test coverage for the gfw.forestchange.forma module."""
# import dev_appserver
# dev_appserver.fix_sys_path()

import itertools
import requests
import unittest
import urllib

from google.appengine.ext import testbed
from contextlib import closing

CDB_URL = 'http://wri-01.cartodb.com/api/v2/sql?%s'


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_urlfetch_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()

    def fetch(self, url):
        with closing(requests.get(url, stream=True)) as r:
            return r

    def getCdbUrl(self, sql):
        return CDB_URL % urllib.urlencode(dict(q=sql))

    def combos(self, params, repeat=None, min=None):
        """Returns a sequence of param tuples (name, value)."""
        result = set()
        if not repeat:
            repeat = len(params) + 1
        if not min:
            min = 1
        for x in range(min, repeat):
            result.update(itertools.combinations(params, x))
        result = list(result)
        result.append(())
        return result
