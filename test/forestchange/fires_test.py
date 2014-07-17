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

from test.forestchange.common import BaseTest

from gfw.forestchange import fires
from gfw.forestchange.fires import execute


class FiresExecuteTest(BaseTest):

    def checkResponse(self, action, data):
        self.assertIsNot(None, action)
        self.assertIsNot(None, data)
        if 'error' in data:
            print 'WARNING - %s' % data['error']
        else:
            self.assertIn('value', data)

    def testWorld(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['geojson'] = '{"type":"Polygon","coordinates":[[[-62.13867187499999,-1.845383988573187],[-64.6875,-7.972197714386866],[-61.083984375,-10.487811882056695],[-52.03125,-5.703447982149503],[-56.77734375,-0.26367094433665017],[-62.13867187499999,-1.845383988573187]]]}'
            action, data = execute(params)
            self.checkResponse(action, data)

    def testNational(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['iso'] = 'idn'
            action, data = execute(params)
            self.checkResponse(action, data)

    def testSubnational(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['iso'] = 'idn'
            params['id1'] = '1'
            action, data = execute(params)
            self.checkResponse(action, data)

    def testWdpa(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['wdpaid'] = '1'
            action, data = execute(params)
            self.checkResponse(action, data)

    def testUse(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            for use in ['logging', 'mining', 'oilpalm', 'fiber']:
                params = dict(params)
                params['useid'] = '1'
                params['use'] = use
                action, data = execute(params)
                self.checkResponse(action, data)

if __name__ == '__main__':
    reload(fires)
    unittest.main(verbosity=2, exit=False)
