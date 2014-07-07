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

from gfw.forestchange import forma
from gfw.forestchange.forma import FormaSql
from gfw.forestchange.forma import execute
from gfw.forestchange import common


class FormaSqlTest(BaseTest):

    """Test FORMA SQL for national, subnational, concessions, and protected
    areas by executing queries for all combinations of args via direct
    requests to CartoDB.
    """

    def testWolrd(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['geojson'] = '{"type":"Polygon","coordinates":[[[-62.13867187499999,-1.845383988573187],[-64.6875,-7.972197714386866],[-61.083984375,-10.487811882056695],[-52.03125,-5.703447982149503],[-56.77734375,-0.26367094433665017],[-62.13867187499999,-1.845383988573187]]]}'
            sql = FormaSql.process(params)
            url = self.getCdbUrl(sql)
            response = self.fetch(url)
            self.assertEqual(200, response.status_code)
            self.assertIsNot(None, response.json()['rows'])
            self.assertIsNot(None, 'value' in response.json()['rows'][0])

    def testNational(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['iso'] = 'idn'
            sql = FormaSql.process(params)
            url = self.getCdbUrl(sql)
            response = self.fetch(url)
            self.assertEqual(200, response.status_code)
            self.assertIsNot(None, response.json()['rows'])
            self.assertIsNot(None, 'value' in response.json()['rows'][0])

    def testSubnational(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['iso'] = 'idn'
            params['id1'] = '1'
            sql = FormaSql.process(params)
            url = self.getCdbUrl(sql)
            response = self.fetch(url)
            self.assertEqual(200, response.status_code)
            self.assertIsNot(None, response.json()['rows'])
            self.assertIsNot(None, 'value' in response.json()['rows'][0])

    def testWdpa(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['wdpaid'] = '1'
            sql = FormaSql.process(params)
            url = self.getCdbUrl(sql)
            response = self.fetch(url)
            self.assertEqual(200, response.status_code)
            self.assertIsNot(None, response.json()['rows'])

    def testUse(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for use in ['mining', 'logging', 'fiber', 'logging']:
            for params in self.combos(args):
                params = dict(args)
                params['useid'] = '1'
                params['use'] = use
                sql = FormaSql.process(params)
                url = self.getCdbUrl(sql)
                response = self.fetch(url)
                self.assertEqual(200, response.status_code)


class FormaExecuteTest(BaseTest):

    def testWorld(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['geojson'] = '{"type":"Polygon","coordinates":[[[-62.1386718 7499999,-1.845383988573187],[-64.6875,-7.972197714386866],[-61.083984375,-10.487811882056695],[-52.03125,-5.703447982149503],[-56.77734375,-0.26367094433665017],[-62.13867187499999,-1.845383988573187]]]}'
            action, data = execute(params)
            self.assertEqual('respond', action)
            self.assertIsNot(None, data)
            self.assertIn('value', data)

    def testNational(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['iso'] = 'idn'
            action, data = execute(params)
            self.assertEqual('respond', action)
            self.assertIsNot(None, data)
            self.assertIn('value', data)

    def testSubnational(self):
        args = [
            ('begin', '2010-01-01'),
            ('end', '2014-01-01')]
        for params in self.combos(args):
            params = dict(params)
            params['iso'] = 'idn'
            params['id1'] = '1'
            action, data = execute(params)
            self.assertEqual('respond', action)
            self.assertIsNot(None, data)
            self.assertIn('value', data)


    # def testWdpa(self):
    #     args = [
    #         ('begin', '2010-01-01'),
    #         ('end', '2014-01-01')]
    #     for params in self.combos(args):
    #         params = dict(params)
    #         params['wdpaid'] = '1'
    #         sql = FormaSql.process(params)
    #         url = self.getCdbUrl(sql)
    #         response = self.fetch(url)
    #         self.assertEqual(200, response.status_code)
    #         self.assertIsNot(None, response.json()['rows'])

    # def testUse(self):
    #     args = [
    #         ('begin', '2010-01-01'),
    #         ('end', '2014-01-01')]
    #     for use in ['mining', 'logging', 'fiber', 'logging']:
    #         for params in self.combos(args):
    #             params = dict(args)
    #             params['useid'] = '1'
    #             params['use'] = use
    #             sql = FormaSql.process(params)
    #             url = self.getCdbUrl(sql)
    #             response = self.fetch(url)
    #             self.assertEqual(200, response.status_code)
#     def testExecuteNational(self):
#         # valid iso
#         action, data = execute(
#             {'iso': 'bra', 'begin': '2001-01-01', 'end': '2014-01-01'})
#         self.assertEqual(action, 'respond')
#         self.assertIn('value', data)
#         self.assertIsNot(data['value'], None)

#         # invalid iso
#         action, data = execute(
#             {'iso': 'FOO', 'begin': '2001-01-01', 'end': '2014-01-01'})
#         self.assertEqual(action, 'respond')
#         self.assertIn('value', data)
#         self.assertEqual(data['value'], None)

#         # no iso
#         self.assertRaises(Exception, execute, {})

if __name__ == '__main__':
    reload(common)
    reload(forma)
    unittest.main(verbosity=2, exit=False)
