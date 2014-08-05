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

"""Unit test coverage for gfw.countries.args"""

from test import common

import unittest

from gfw.countries import args


class PathProcessorTest(common.BaseTest):

    def test_process_path(self):
        path = '/countries/bra'
        value = args.process_path(path, 'iso')
        self.assertEqual({'iso': 'bra'}, value)

        path = '/countries/bra/123'
        value = args.process_path(path, 'id1')
        self.assertEqual({'iso': 'bra', 'id1': '123'}, value)


class ArgsTest(common.BaseTest):

    def test_bust(self):
        f = args.ArgProcessor.bust
        self.assertTrue(f('bust')['bust'])

    def test_dev(self):
        f = args.ArgProcessor.dev
        self.assertTrue(f('dev')['dev'])

    def test_process(self):
        f = args.ArgProcessor.process
        params = {
            "bust": 1,
            "dev": 1,
            "thresh": 25
        }
        x = f(params)
        self.assertItemsEqual(['thresh', 'dev', 'bust'], x)

if __name__ == '__main__':
    unittest.main(exit=False)
