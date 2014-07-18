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

"""Unit test coverage for the gfw.countries module."""

import unittest

from test.forestchange.common import BaseTest

from gfw.countries import countries


class CountriesTest(BaseTest):

    def testExecute(self):
        action, data = countries.execute(dict(iso='bra'))
        self.assertEqual(action, 'respond')
        self.assertNotEqual(data, None)
        for key in ['topojson', 'bounds', 'subnat_bounds', 'forma', 'tenure',
                    'umd']:
            self.assertIn(key, data)
            self.assertNotEqual(data[key], None)


if __name__ == '__main__':

    unittest.main(verbosity=2, exit=False)
