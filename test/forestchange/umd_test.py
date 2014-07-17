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

from test.forestchange.common import BaseTest

from gfw.forestchange import umd
from gfw.forestchange.umd import execute


class UmdExecuteTest(BaseTest):

    def checkResponse(self, action, data):
        self.assertIsNot(None, action)
        self.assertIsNot(None, data)
        if 'error' in data:
            print 'WARNING - %s' % data['error']
        else:
            self.assertIn('years', data)

    def testNational(self):
        action, data = execute({'iso': 'bra', 'thresh': 10})
        self.checkResponse(action, data)

    def testSubnational(self):
        action, data = execute({'iso': 'bra', 'id1': 1, 'thresh': 10})
        self.checkResponse(action, data)

if __name__ == '__main__':
    reload(umd)
    unittest.main(verbosity=2, exit=False)
