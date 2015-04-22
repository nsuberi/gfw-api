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

"""This module supports acessing FORMA data."""

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql


class FormaSql(Sql):

    WORLD = """
        SELECT COUNT(f.*) AS value
        FROM forma_api f
        WHERE f.{date_column} >= '{begin}'::date
              AND f.{date_column} <= '{end}'::date
              AND ST_INTERSECTS(
                ST_SetSRID(
                  ST_GeomFromGeoJSON('{geojson}'), 4326), f.the_geom)"""

    ISO = """
        SELECT COUNT(f.*) AS value
        FROM forma_api f
        WHERE f.{date_column} >= '{begin}'::date
              AND f.{date_column} <= '{end}'::date
              AND f.iso = UPPER('{iso}')"""

    ID1 = """
        SELECT COUNT(f.*) AS value
        FROM forma_api f
        INNER JOIN (
            SELECT *
            FROM gadm2
            WHERE id_1 = {id1}
                  AND iso = UPPER('{iso}')) g
            ON f.gadm2::int = g.objectid
        WHERE f.{date_column} >= '{begin}'::date
              AND f.{date_column} <= '{end}'::date"""

    WDPA = """
        SELECT COUNT(f.*) AS value
        FROM forma_api f, (SELECT * FROM protected_areas WHERE wdpaid={wdpaid}) AS p
        WHERE ST_Intersects(f.the_geom, p.the_geom)
              AND f.date >= '{begin}'::date
              AND f.date <= '{end}'::date"""

    USE = """
        SELECT COUNT(f.*) AS value
        FROM {use_table} u, forma_api f
        WHERE u.cartodb_id = {pid}
              AND ST_Intersects(f.the_geom, u.the_geom)
              AND f.date >= '{begin}'::date
              AND f.date <= '{end}'::date"""

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


def execute(args):
    args['version'] = 'v1'
    action, data = CartoDbExecutor.execute(args, FormaSql)
    if action == 'redirect' or action == 'error':
        return action, data
    return _processResults(action, data)
