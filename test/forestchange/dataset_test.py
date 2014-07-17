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

"""Unit test coverage the execute function on all dataset modules."""

import unittest

from test.forestchange.common import BaseTest

from gfw.forestchange import fires
from gfw.forestchange import umd
from gfw.forestchange import forma
from gfw.forestchange import imazon
from gfw.forestchange import quicc

DATASETS = [fires, umd, forma, imazon, quicc]


class DatasetExecuteTest(BaseTest):

    def checkResponse(self, action, data):
        self.assertIsNot(None, action)
        self.assertIsNot(None, data)
        if 'error' in data:
            print 'WARNING - %s' % data['error']
        else:
            # years for umd, value for others...
            self.assertTrue('value' in data or 'years' in data)

    def testWorld(self):
        map(self._testWorld, [fires, forma, imazon, quicc])

    def _testWorld(self, dataset):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['geojson'] = '{"type":"Polygon","coordinates":[[[-62.13867187499999,-1.845383988573187],[-64.6875,-7.972197714386866],[-61.083984375,-10.487811882056695],[-52.03125,-5.703447982149503],[-56.77734375,-0.26367094433665017],[-62.13867187499999,-1.845383988573187]]]}'
            action, data = dataset.execute(params)
            self.checkResponse(action, data)

    def testNational(self):
        map(self._testNational, DATASETS)

    def _testNational(self, dataset):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['iso'] = 'idn'
            action, data = dataset.execute(params)
            self.checkResponse(action, data)

    def testSubnational(self):
        map(self._testSubnational, DATASETS)

    def _testSubnational(self, dataset):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['iso'] = 'idn'
            params['id1'] = '1'
            action, data = dataset.execute(params)
            self.checkResponse(action, data)

    def testWdpa(self):
        map(self._testWorld, [fires, forma, imazon, quicc])

    def _testWdpa(self, dataset):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['wdpaid'] = '1'
            action, data = dataset.execute(params)
            self.checkResponse(action, data)

    def testUse(self):
        map(self._testWorld, [fires, forma, imazon, quicc])

    def _testUse(self, dataset):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            for use in ['logging', 'mining', 'oilpalm', 'fiber']:
                params = dict(params)
                params['useid'] = '1'
                params['use'] = use
                action, data = dataset.execute(params)
                self.checkResponse(action, data)

if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
