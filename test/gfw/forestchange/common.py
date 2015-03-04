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

"""Unit test coverage for the gfw.forestchange.api module.

These test the actual RequestHandlers in the api module for both analysis
and download queries. This doesn't test the CartoDB SQL used. See the
test/gfw.forestchange.sql for that.
"""

from test import common

import unittest
import webapp2
import webtest

from gfw.forestchange import api


class BaseApiTest(common.FetchBaseTest):

    def setUp(self):
        super(BaseApiTest, self).setUp()
        app = webapp2.WSGIApplication([(r'/forest-change.*', api.Handler)])
        self.api = webtest.TestApp(app)
        self.args = [
            ('bust', 1),
            ('dev', 1),
            ('period', '2008-01-01,2014-01-01')]

    def _testGetNational(self, dataset):
        path = r'/forest-change/%s/admin/bra' % dataset

        for combo in common.combos(self.args):
            args = dict(combo)
            cdb_response = '{"rows":[{"value":9870}]}'
            self.setResponse(content=cdb_response, status_code=200)
            r = self.api.get(path, args)
            self.assertTrue('value' in r.json or 'years' in r.json)
            self.assertIn('params', r.json)
            self.assertIn('iso', r.json['params'])
            self.assertEqual(200, r.status_code)

    def _testGetSubnational(self, dataset):
        path = r'/forest-change/%s/admin/bra/2' % dataset

        for combo in common.combos(self.args):
            args = dict(combo)
            cdb_response = '{"rows":[{"value":9870}]}'
            self.setResponse(content=cdb_response, status_code=200)
            r = self.api.get(path, args)
            self.assertIn('value', r.json)
            self.assertIn('params', r.json)
            self.assertIn('iso', r.json['params'])
            self.assertEqual(r.json['params']['iso'], 'bra')
            self.assertIn('id1', r.json['params'])
            self.assertEqual(r.json['params']['id1'], '2')
            self.assertEqual(200, r.status_code)

    def _testGetWdpa(self, dataset):
        path = r'/forest-change/%s/wdpa/180' % dataset

        for combo in common.combos(self.args):
            args = dict(combo)
            cdb_response = '{"rows":[{"value":9870}]}'
            self.setResponse(content=cdb_response, status_code=200)
            r = self.api.get(path, args)
            self.assertIn('value', r.json)
            self.assertIn('params', r.json)
            self.assertIn('wdpaid', r.json['params'])
            self.assertEqual(r.json['params']['wdpaid'], '180')
            self.assertEqual(200, r.status_code)

    def _testGetUse(self, dataset):
        path = r'/forest-change/%s/use/%s/1'

        for use in ['logging', 'oilpalm', 'fiber', 'mining']:
            p = path % (use, dataset)
            for combo in common.combos(self.args):
                args = dict(combo)
                cdb_response = '{"rows":[{"value":9870}]}'
                self.setResponse(content=cdb_response, status_code=200)
                r = self.api.get(p, args)
                self.assertIn('value', r.json)
                self.assertIn('params', r.json)
                self.assertIn('use', r.json['params'])
                self.assertEqual(r.json['params']['use'], use)
                self.assertIn('useid', r.json['params'])
                self.assertEqual(r.json['params']['useid'], '1')
                self.assertEqual(200, r.status_code)


class FormaApiTest(BaseApiTest):

    def testGetNational(self):
        self._testGetNational('forma-alerts')

    def testGetSubnational(self):
        self._testGetNational('forma-alerts')

    def testGetWdpa(self):
        self._testGetNational('forma-alerts')

    def testGetUse(self):
        self._testGetNational('forma-alerts')


class FiresApiTest(BaseApiTest):

    def testGetNational(self):
        self._testGetNational('nasa-active-fires')

    def testGetSubnational(self):
        self._testGetNational('nasa-active-fires')

    def testGetWdpa(self):
        self._testGetNational('nasa-active-fires')

    def testGetUse(self):
        self._testGetNational('nasa-active-fires')


class QuiccApiTest(BaseApiTest):

    def testGetNational(self):
        self._testGetNational('quicc-alerts')

    def testGetSubnational(self):
        self._testGetNational('quicc-alerts')

    def testGetWdpa(self):
        self._testGetNational('quicc-alerts')

    def testGetUse(self):
        self._testGetNational('quicc-alerts')


class ImazonApiTest(BaseApiTest):

    def testGetNational(self):
        self._testGetNational('imazon-alerts')

    def testGetSubnational(self):
        self._testGetNational('imazon-alerts')

    def testGetWdpa(self):
        self._testGetNational('imazon-alerts')

    def testGetUse(self):
        self._testGetNational('imazon-alerts')


class UmdApiTest(BaseApiTest):

    def testGetNational(self):
        self._testGetNational('umd-loss-gain')

    def testGetSubnational(self):
        self._testGetNational('umd-loss-gain')

class TerraiApiTest(BaseApiTest):

    def testGetNational(self):
        self._testGetNational('terrai-alerts')

    def testGetSubnational(self):
        self._testGetNational('terrai-alerts')

    def testGetWdpa(self):
        self._testGetNational('terrai-alerts')

    def testGetUse(self):
        self._testGetNational('terrai-alerts')


class FunctionTest(unittest.TestCase):

    """Test for the FormaIsoHandler."""

    def setUp(self):
        self.args = [
            ('bust', 1),
            ('period', '2008-01-01,2009-01-01')]

    def test_dataset_from_path(self):
        path = '/forest-change/forma-alerts/admin/bra'
        dataset = api._dataset_from_path(path)

        self.assertEqual('forma-alerts', dataset)

        path = '/forest-change/forma-alerts'
        dataset = api._dataset_from_path(path)

    def test_classify_request(self):
        path = '/forest-change/forma-alerts'
        self.assertEqual(('forma-alerts', 'all'), api._classify_request(path))

        path = '/forest-change/forma-alerts/admin/bra'
        self.assertEqual(('forma-alerts', 'iso'), api._classify_request(path))

        path = '/forest-change/forma-alerts/admin/bra/123'
        self.assertEqual(('forma-alerts', 'id1'), api._classify_request(path))

        path = '/forest-change/forma-alerts/wdpa/123'
        self.assertEqual(('forma-alerts', 'wdpa'), api._classify_request(path))

if __name__ == '__main__':
    unittest.main(exit=False, failfast=True)
