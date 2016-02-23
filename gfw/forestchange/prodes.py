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

"""This module supports acessing PRODES data."""

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql


class ProdesSql(Sql):

    WORLD = """
        SELECT round(sum(f.areameters)/10000) AS value
            {additional_select}
        FROM prodes_wgs84 f
        WHERE to_date(f.ano, 'YYYY') >= '{begin}'::date
              AND to_date(f.ano, 'YYYY') < '{end}'::date
              AND ST_INTERSECTS(
                ST_SetSRID(
                  ST_GeomFromGeoJSON('{geojson}'), 4326), f.the_geom)
        """

    ISO = """
        with s as (
            SELECT st_simplify(the_geom, 0.0001) as the_geom 
            FROM gadm2_provinces_simple
            WHERE iso = UPPER('{iso}'))
        SELECT round(sum(f.areameters)/10000) AS value
            {additional_select}
        FROM prodes_wgs84 f, s
        WHERE  to_date(f.ano, 'YYYY') >= '{begin}'::date
        AND to_date(f.ano, 'YYYY') < '{end}'::date
        AND st_intersects(f.the_geom, s.the_geom)
        """

    ID1 = """
        with s as (
            SELECT st_simplify(the_geom, 0.0001) as the_geom
            FROM gadm2_provinces_simple
            WHERE iso = UPPER('{iso}') AND id_1 = {id1})
        SELECT round(sum(f.areameters)/10000) AS value
		{additional_select}
        FROM prodes_wgs84 f, s
        WHERE  to_date(f.ano, 'YYYY') >= '{begin}'::date
        AND to_date(f.ano, 'YYYY') < '{end}'::date
        AND st_intersects(f.the_geom, s.the_geom)

        """

    WDPA = """
        SELECT round(sum(f.areameters)/10000) AS value
            {additional_select}
        FROM prodes_wgs84 f, (SELECT CASE when marine::numeric = 2 then null
        when ST_NPoints(the_geom)<=18000 THEN the_geom
       WHEN ST_NPoints(the_geom) BETWEEN 18000 AND 50000 THEN ST_RemoveRepeatedPoints(the_geom, 0.001)
      ELSE ST_RemoveRepeatedPoints(the_geom, 0.005)
       END as the_geom FROM wdpa_protected_areas where wdpaid={wdpaid}) AS p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
              and to_date(f.ano, 'YYYY') >= '{begin}'::date
              AND to_date(f.ano, 'YYYY') < '{end}'::date
        """

    USE = """
        SELECT round(sum(f.areameters)/10000) AS value
            {additional_select}
        FROM {use_table} u, prodes_wgs84 f
        WHERE u.cartodb_id = {pid}
              AND ST_Intersects(f.the_geom, u.the_geom)
              AND to_date(f.ano, 'YYYY') >= '{begin}'::date
              AND to_date(f.ano, 'YYYY') < '{end}'::date
        """

    LATEST = """
        SELECT DISTINCT ano
        FROM prodes_wgs84
        WHERE ano IS NOT NULL
        ORDER BY ano DESC
        LIMIT {limit}"""

    @classmethod
    def download(cls, sql):
        download_sql = sql.replace(ProdesSql.MIN_MAX_DATE_SQL, "")
        download_sql = download_sql.replace("SELECT round(sum(f.areameters)/10000) AS value", "SELECT f.*")
        return ' '.join(
            download_sql.split())


def _processResults(action, data):
    if 'rows' in data:
        results = data.pop('rows')
        result = results[0]
        if not result.get('value'):
            data['results'] = results
    else:
        result = dict(value=None, min_date=None, max_date=None)

    data['value'] = result.get('value')
    data['min_date'] = result.get('min_date')
    data['max_date'] = result.get('max_date')

    return action, data


def execute(args):
    args['version'] = 'v1'
    action, data = CartoDbExecutor.execute(args, ProdesSql)
    if action == 'redirect' or action == 'error':
        return action, data
    return _processResults(action, data)
