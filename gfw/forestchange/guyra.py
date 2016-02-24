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

class GuyraSql(Sql):

    MIN_MAX_DATE_SQL = ""

    WORLD = """
        SELECT sum(sup) AS value, MIN(date) as min_date, MAX(date) as max_date
        FROM gran_chaco_deforestation f
        WHERE date >= '{begin}'::date
              AND date <= '{end}'::date
              AND ST_INTERSECTS(
                ST_SetSRID(
                  ST_GeomFromGeoJSON('{geojson}'), 4326), f.the_geom)
        """

    ISO = """
        with r as (SELECT date,pais,sup, prov_dep FROM gran_chaco_deforestation),
              d as (SELECT name_1,iso, id_1, name_0 FROM gadm2_provinces_simple), 
              f as (select * from r inner join f on prov_dep=name_1)
        SELECT sum(sup) AS value, MIN(date) as min_date, MAX(date) as max_date   
        FROM f
        WHERE iso = UPPER('{iso}')
            AND date >= '{begin}'::date
            AND date <= '{end}'::date
        """

    ID1 = """
        with r as (SELECT date,pais,sup, prov_dep FROM gran_chaco_deforestation),
              d as (SELECT name_1,iso, id_1, name_0 FROM gadm2_provinces_simple), 
              f as (select * from r inner join f on prov_dep=name_1)
        SELECT sum(sup) AS value, MIN(date) as min_date, MAX(date) as max_date
        FROM f
        WHERE iso = UPPER('{iso}')
            AND id_1 = {id1}
            AND date >= '{begin}'::date
            AND date <= '{end}'::date
        """

    WDPA = """
        WITH p as (SELECT CASE when marine::numeric = 2 then null
        when ST_NPoints(the_geom)<=18000 THEN the_geom
       WHEN ST_NPoints(the_geom) BETWEEN 18000 AND 50000 THEN ST_RemoveRepeatedPoints(the_geom, 0.001)
      ELSE ST_RemoveRepeatedPoints(the_geom, 0.005)
       END as the_geom FROM wdpa_protected_areas where wdpaid={wdpaid})
        SELECT sum(sup) AS value, MIN(date) as min_date, MAX(date) as max_date
        FROM gran_chaco_deforestation f, p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
              AND date >= '{begin}'::date
              AND date <= '{end}'::date
        """

    USE = """
        SELECT sum(sup) AS value, MIN(date) as min_date, MAX(date) as max_date
        FROM {use_table} u, gran_chaco_deforestation f
        WHERE u.cartodb_id = {pid}
              AND ST_Intersects(f.the_geom, u.the_geom)
              AND date >= '{begin}'::date
              AND date <= '{end}'::date
        """

    LATEST = """
        SELECT DISTINCT time
        FROM gran_chaco_deforestation 
        ORDER BY time DESC
        LIMIT {limit}"""

    @classmethod
    def download(cls, sql):
        download_sql = sql.replace(GuyraSql.MIN_MAX_DATE_SQL, "")
        download_sql = download_sql.replace("sum(sup) AS value, MIN(date) as min_date, MAX(date) as max_date", "f.*")
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
    data['min_date'] = result.get('min_date')
    data['max_date'] = result.get('max_date')
    return action, data


def execute(args):
    args['version'] = 'v2'
    action, data = CartoDbExecutor.execute(args, GuyraSql)
    if action == 'redirect' or action == 'error':
        return action, data
    return _processResults(action, data)
