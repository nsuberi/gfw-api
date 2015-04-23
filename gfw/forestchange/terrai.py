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

"""This module supports acessing TERRAI data."""

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql

class TerraiSql(Sql):

    WORLD = """
        SELECT COUNT(f.*) AS value
        {additional_select}
        FROM terra_i_decrease f
        WHERE {max_min_selector} >= '{begin}'::date
              AND {max_min_selector} <= '{end}'::date
              AND ST_INTERSECTS(
                ST_SetSRID(
                  ST_GeomFromGeoJSON('{geojson}'), 4326), f.the_geom)"""

    ISO = """
        SELECT COUNT(f.*) AS value
        {additional_select}
        FROM terra_i_decrease f
        WHERE iso = UPPER('{iso}')
            AND {max_min_selector} >= '{begin}'::date
            AND {max_min_selector} <= '{end}'::date"""

    ID1 = """
        SELECT COUNT(f.*) AS value
        {additional_select}
        FROM terra_i_decrease f,
            (SELECT * FROM gadm2_provinces_simple
             WHERE iso = UPPER('{iso}') AND id_1 = {id1}) as p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
            AND {max_min_selector} >= '{begin}'::date
            AND {max_min_selector} <= '{end}'::date"""

    WDPA = """
        SELECT COUNT(f.*) AS value
        FROM terra_i_decrease f, (SELECT * FROM wdpa_all WHERE wdpaid={wdpaid}) AS p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
              AND DATE ((2004+FLOOR((f.grid_code-1)/23))::text || '-01-01') +  (MOD(f.grid_code,23)*16 ) >= '{begin}'::date
              AND DATE ((2004+FLOOR((f.grid_code-1)/23))::text || '-01-01') +  (MOD(f.grid_code,23)*16 ) <= '{end}'::date"""

    USE = """
        SELECT COUNT(f.*) AS value
        FROM {use_table} u, terra_i_decrease f
        WHERE u.cartodb_id = {pid}
              AND ST_Intersects(f.the_geom, u.the_geom)
              AND DATE ((2004+FLOOR((f.grid_code-1)/23))::text || '-01-01') +  (MOD(f.grid_code,23)*16 ) >= '{begin}'::date
              AND DATE ((2004+FLOOR((f.grid_code-1)/23))::text || '-01-01') +  (MOD(f.grid_code,23)*16 ) <= '{end}'::date"""

    @classmethod
    def download(cls, sql):
        return ' '.join(
            sql.replace("SELECT COUNT(f.*) AS value", "SELECT f.*").split())


def _processResults(action, data):
    if 'rows' in data:
        result = data['rows'][0]
        data.pop('rows')
    else:
        result = dict(value=None)

    data['value'] = result['value']

    return action, data

def _maxMinSelector(args):
    if args.get('alert_query'):
        return 'f.created_at'
    else: 
        return "DATE ((2004+FLOOR((f.grid_code-1)/23))::text || '-01-01') +  (MOD(f.grid_code,23)*16 )"

def execute(args):
    args['version'] = 'v2'
    args['max_min_selector'] = _maxMinSelector(args)
    action, data = CartoDbExecutor.execute(args, TerraiSql)
    if action == 'redirect' or action == 'error':
        return action, data
    return _processResults(action, data)
