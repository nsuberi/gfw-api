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

    MIN_MAX_DATE_SQL = ", MIN(date) as min_date, MAX(date) as max_date"

    WORLD = """
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM latin_decrease_current_points f
        WHERE date >= '{begin}'::date
              AND date <= '{end}'::date
              AND ST_INTERSECTS(
                ST_SetSRID(
                  ST_GeomFromGeoJSON('{geojson}'), 4326), f.the_geom)
        """

    ISO = """
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM latin_decrease_current_points f
        WHERE iso = UPPER('{iso}')
            AND date >= '{begin}'::date
            AND date <= '{end}'::date
        """

    ID1 = """
        WITH p as (SELECT st_simplify (the_geom, 0.0001) as the_geom FROM gadm2_provinces_simple
            WHERE iso = UPPER('{iso}') AND id_1 = {id1} LIMIT 1)
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM latin_decrease_current_points f,p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
            AND date >= '{begin}'::date
            AND date <= '{end}'::date
        """

    WDPA = """
        WITH p as (SELECT st_simplify (the_geom, 0.0001) as the_geom FROM wdpa_protected_areas
            WHERE wdpaid={wdpaid} LIMIT 1)
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM latin_decrease_current_points f, p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
              AND date >= '{begin}'::date
              AND date <= '{end}'::date
        """

    USE = """
        SELECT 
            COUNT(f.*) AS value
            {additional_select}
        FROM {use_table} u, latin_decrease_current_points f
        WHERE u.cartodb_id = {pid}
              AND ST_Intersects(f.the_geom, u.the_geom)
              AND date >= '{begin}'::date
              AND date <= '{end}'::date
        """

    LATEST = """
        SELECT DISTINCT
            grid_code,
            date
        FROM latin_decrease_current_points 
        WHERE grid_code IS NOT NULL
        GROUP BY grid_code
        ORDER BY grid_code DESC
        LIMIT {limit}"""

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
