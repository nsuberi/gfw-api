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

from test import common
from test.gfw.forestchange import sqls

import unittest

from gfw.forestchange import fires
from gfw.forestchange import umd
from gfw.forestchange import forma
from gfw.forestchange import imazon
from gfw.forestchange import quicc

DATASETS = [fires, umd, forma, imazon, quicc]


class FormaSqlTest(unittest.TestCase):

    """Test SQL generation for FORMA queries."""

    def testFormaSql(self):

        # World
        sql = forma.FormaSql.process({'geojson': 'foo'})[0]
        self.assertEqual(sql, sqls.forma_world)

        # National
        sql = forma.FormaSql.process({'iso': 'bra'})[0]
        self.assertEqual(sql, sqls.forma_national)

        # Subnational
        sql = forma.FormaSql.process({'iso': 'bra', 'id1': 1})[0]
        self.assertEqual(sql, sqls.forma_subnational)

        # WDPA
        sql = forma.FormaSql.process({'wdpaid': 1})[0]
        self.assertEqual(sql, sqls.forma_wdpa)

        # Use
        sql = forma.FormaSql.process({'use': 'logging', 'useid': 1})[0]
        self.assertEqual(sql, sqls.forma_use)

        # Dates
        sql = forma.FormaSql.process({'geojson': 'foo', 'begin': 'foo'})[0]
        self.assertEqual(sql, sqls.forma_begin)

        sql = forma.FormaSql.process({'geojson': 'foo', 'end': 'foo'})[0]
        self.assertEqual(sql, sqls.forma_end)

        sql = forma.FormaSql.process(
            {'geojson': 'foo', 'end': 'foo', 'begin': 'foo'})[0]
        self.assertEqual(sql, sqls.forma_begin_end)


class FormaExecuteTest(common.FetchBaseTest):

    def testWorld(self):

        # World success
        args = {'geojson': '"json"'}
        cdb_response = '{"rows":[{"value":9870}]}'
        self.setResponse(content=cdb_response, status_code=200)
        action, data = forma.execute(args)
        self.assertEqual(action, 'respond')
        self.assertEqual(data['value'], 9870)
        self.assertEqual(data['params'], args)

        # World failure
        args = {'geojson': '"json"'}
        cdb_response = '{"error":["oops"]}'
        self.setResponse(content=cdb_response, status_code=400)
        action, data = forma.execute(args)
        self.assertEqual(action, 'error')
        self.assertEqual(data['error'],  'CartoDB Error: %s' % cdb_response)
        self.assertEqual(data['params'], args)

        return

if __name__ == '__main__':
    unittest.main(verbosity=2, exit=False)
