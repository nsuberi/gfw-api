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

"""This module supports accessing UMD/GLAD data."""
import math
import arrow
import logging

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql

class GladSql(Sql):

    WORLD = """
        SELECT COUNT(iso) AS value, MIN(date) as min_date, MAX(date) as max_date
        FROM  umd_alerts_agg_analysis f
        WHERE date >= '{begin}'::date
          AND date <= '{end}'::date
          AND ST_INTERSECTS(
                ST_Transform(
                  ST_SetSRID(
                    ST_GeomFromGeoJSON('{geojson}'),
                  4326),
                3857),
              f.the_geom_webmercator)
        """

    ISO = """
        SELECT COUNT(iso) AS value, MIN(date) as min_date, MAX(date) as max_date
        FROM umd_alerts_agg_analysis f
        WHERE iso = UPPER('{iso}')
            AND date >= '{begin}'::date
            AND date <= '{end}'::date
        """

    ID1 = """
        WITH r as (SELECT name_1,iso, id_1, the_geom_webmercator 
                   FROM gadm2_provinces_simple 
                   WHERE iso = UPPER('{iso}') 
                   AND id_1 = {id1} )
        SELECT COUNT(iso) AS value, MIN(date) as min_date, MAX(date) as max_date  
        FROM umd_alerts_agg_analysis f INNER JOIN r ON st_intersects(r.the_geom_webmercator,f.the_geom_webmercator)
        WHERE date >= '{begin}'::date 
        AND date <= '{end}'::date
        """

    WDPA = """
        WITH p as (SELECT CASE when marine::numeric = 2 then null
        when ST_NPoints(the_geom)<=18000 THEN the_geom_webmercator
       WHEN ST_NPoints(the_geom) BETWEEN 18000 AND 50000 THEN ST_RemoveRepeatedPoints(the_geom_webmercator, 100)
      ELSE ST_RemoveRepeatedPoints(the_geom_webmercator, 1000)
       END as the_geom_webmercator FROM wdpa_protected_areas where wdpaid={wdpaid})
        SELECT COUNT(iso) AS value, MIN(date) as min_date, MAX(date) as max_date
        FROM umd_alerts_agg_analysis f, p
        WHERE ST_Intersects(f.the_geom_webmercator, p.the_geom_webmercator)
              AND date >= '{begin}'::date
              AND date <= '{end}'::date
        """

    USE = """
        SELECT COUNT(iso) AS value, MIN(date) as min_date, MAX(date) as max_date
        FROM {use_table} u, umd_alerts_agg_analysis f
        WHERE u.cartodb_id = {pid}
              AND ST_Intersects(f.the_geom_webmercator, u.the_geom_webmercator)
              AND date >= '{begin}'::date
              AND date <= '{end}'::date
        """

    LATEST = """
        SELECT DISTINCT date
        FROM umd_alerts_agg_analysis
        ORDER BY date DESC
        LIMIT {limit}"""

    @classmethod
    def download(cls, sql):
        return sql.replace("COUNT(iso) AS value, MIN(date) as min_date, MAX(date) as max_date", " f.date, st_transform(f.the_geom_webmercator, 4326) as the_geom, ST_Y(st_transform(the_geom_webmercator, 4326)) as lat, ST_X(st_transform(the_geom_webmercator, 4326)) as long")

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
    action, data = CartoDbExecutor.execute(args, GladSql)
    if action == 'redirect' or action == 'error':
        return action, data
    return _processResults(action, data)
