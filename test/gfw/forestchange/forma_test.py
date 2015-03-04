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

import mock


from gfw.forestchange import forma


class FormaSqlTest(common.FetchBaseTest):

    def setUp(self):
        self.args = {
            'useid':'1234'
        }
        self.params = {
            'fake_parameter' : 'fake123',
            'begin':'2000-01-01',
            'end':'2010-01-01'
        }
        self.USE = "fp: {fake_parameter} --- {use_table}"

    @mock.patch('gfw.forestchange.forma.FormaSql.get_query_type')
    def testUseWithConsessionKey(self,mock_get_query_type):
        args = self.args.copy()
        args['use'] = 'mining'
        forma.FormaSql.USE = self.USE
        correct_params = self.params.copy()
        correct_params['use_table'] = 'gfw_mining'
        correct_params['pid'] = args['useid']
        mock_get_query_type.return_value = ('fake-type', self.params)
        query, download_query = forma.FormaSql.use(self.params,args)
        mock_get_query_type.assert_called_with(correct_params,args)
        self.assertEqual(self.USE.format(**correct_params),query)



    @mock.patch('gfw.forestchange.forma.FormaSql.get_query_type')
    def testUseWithGenericTable(self,mock_get_query_type):
        args = self.args.copy()
        args['use'] = 'generic'
        forma.FormaSql.USE = self.USE
        correct_params = self.params.copy()
        correct_params['use_table'] = 'generic'
        correct_params['pid'] = args['useid']
        mock_get_query_type.return_value = ('fake-type', self.params)
        query, download_query = forma.FormaSql.use(self.params,args)
        mock_get_query_type.assert_called_with(correct_params,args)
        self.assertEqual(self.USE.format(**correct_params),query)


if __name__ == '__main__':
    unittest.main(exit=False, failfast=True)
