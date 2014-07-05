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

import unittest

from google.appengine.ext import testbed

from gfw.forestchange import forma
from gfw.forestchange import common


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


class FormaTest(BaseTest):

    def testNationalSql(self):
        sql = forma.FormaSql.process(
            {'iso': 'bra', 'begin': '2001', 'end': '2002'})
        self.assertTrue("iso = UPPER('bra')" in sql)
        self.assertTrue("date >= '2001'::date" in sql)
        self.assertTrue("date <= '2002'::date" in sql)

    def testSubnationalSql(self):
        sql = forma.FormaSql.process(
            {'iso': 'bra', 'id1': '1', 'begin': '2001', 'end': '2002'})
        self.assertTrue("iso = UPPER('bra')" in sql)
        self.assertTrue("id_1 = 1" in sql)
        self.assertTrue("date >= '2001'::date" in sql)
        self.assertTrue("date <= '2002'::date" in sql)

    def testExecuteNational(self):
        # valid iso
        action, data = forma.execute(
            {'iso': 'bra', 'begin': '2001-01-01', 'end': '2014-01-01'})
        self.assertEqual(action, 'respond')
        self.assertIn('value', data)
        self.assertIsNot(data['value'], None)

        # invalid iso
        action, data = forma.execute(
            {'iso': 'FOO', 'begin': '2001-01-01', 'end': '2014-01-01'})
        self.assertEqual(action, 'respond')
        self.assertIn('value', data)
        self.assertEqual(data['value'], None)

        # no iso
        self.assertRaises(Exception, forma.execute, {})

if __name__ == '__main__':
    reload(common)
    reload(forma)
    unittest.main(verbosity=2, exit=False)
