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
import math
import arrow

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql

class TerraiSql(Sql):

    DATE = "DATE ((2004+FLOOR((f.grid_code-1)/23))::text || '-01-01') +  (MOD(f.grid_code,23)*16 )"
    MIN_MAX_DATE_SQL = ", MIN(%s) as min_date, MAX(%s) as max_date" % (DATE,DATE)

    WORLD = """
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM latin_decrease_current_points f
        WHERE %s >= '{begin}'::date
              AND %s <= '{end}'::date
              AND ST_INTERSECTS(
                ST_SetSRID(
                  ST_GeomFromGeoJSON('{geojson}'), 4326), f.the_geom)
        """ % (DATE,DATE)

    ISO = """
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM latin_decrease_current_points f
        WHERE iso = UPPER('{iso}')
            AND %s >= '{begin}'::date
            AND %s <= '{end}'::date
        """  % (DATE,DATE)

    ID1 = """
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM latin_decrease_current_points f,
            (SELECT * FROM gadm2_provinces_simple
             WHERE iso = UPPER('{iso}') AND id_1 = {id1}) as p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
            AND %s >= '{begin}'::date
            AND %s <= '{end}'::date
        """  % (DATE,DATE)

    WDPA = """
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM latin_decrease_current_points f, (SELECT * FROM wdpa_all WHERE wdpaid={wdpaid}) AS p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
              AND %s >= '{begin}'::date
              AND %s <= '{end}'::date
        """  % (DATE,DATE)

    USE = """
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM {use_table} u, latin_decrease_current_points f
        WHERE u.cartodb_id = {pid}
              AND ST_Intersects(f.the_geom, u.the_geom)
              AND %s >= '{begin}'::date
              AND %s <= '{end}'::date
        """  % (DATE,DATE)

    LATEST = """
        SELECT DISTINCT
            grid_code,
            %s as date
        FROM latin_decrease_current_points 
        WHERE grid_code IS NOT NULL
        GROUP BY grid_code
        ORDER BY grid_code DESC
        LIMIT {limit}""" % (DATE)

    @classmethod
    def download(cls, sql):
        download_sql = sql.replace(TerraiSql.MIN_MAX_DATE_SQL, "")
        download_sql = download_sql.replace("SELECT COUNT(f.*) AS value", "SELECT f.*")
        return ' '.join(
            download_sql.split())


def _processResults(action, data):
    if 'rows' in data:
        results = data.pop('rows')
        result = results[0]
        if not result.get('value'):
            data['results'] = results
    else:
        result = dict(value=None)
    data['value'] = result.get('value')
    data['min_date'] = _gridCodeToDate(result.get('min_grid_code'))
    data['max_date'] = _gridCodeToDate(result.get('max_grid_code'))
    return action, data

def _gridCodeToDate(grid_code):
    if grid_code:
        year = 2004 + math.floor((grid_code-1)/23)
        first_of_year = arrow.get(('%s-01-01' % year))
        periods = math.fmod(grid_code,23) * 16
        date = first_of_year.replace(days=+periods)
        return date.format('YYYY-MM-DD')
    else:
        return None

def execute(args):
    args['version'] = 'v2'
    action, data = CartoDbExecutor.execute(args, TerraiSql)
    if action == 'redirect' or action == 'error':
        return action, data
    return _processResults(action, data)
