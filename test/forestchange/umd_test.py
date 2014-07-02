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

"""Unit test coverage for the gfw.forestchange.umd module."""

import unittest

from google.appengine.ext import testbed

from gfw.forestchange import umd, common


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


class UmdTest(BaseTest):

    def testSql(self):
        sql = umd.UmdSql.process({'iso': 'bra', 'thresh': 10})
        self.assertTrue("iso = UPPER('bra')" in sql)
        self.assertTrue("thresh = 10" in sql)

    def testIso(self):
        action, data = umd.execute({'iso': 'bra', 'thresh': 10})
        self.assertEqual(action, 'respond')
        print data

if __name__ == '__main__':
    reload(common)
    reload(umd)
    unittest.main(verbosity=2, exit=False)
