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

"""This module supports acessing NASA QUICC alert data."""

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql


class QuiccSql(Sql):

    WORLD = """
        SELECT count(pt.*) AS value
        FROM modis_forest_change_copy pt
        WHERE pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date
            AND ST_INTERSECTS(
                ST_SetSRID(ST_GeomFromGeoJSON('{geojson}'), 4326), the_geom)"""

    ISO = """
        SELECT p.iso, count(pt.*) AS value
        FROM modis_forest_change_copy pt,
            (SELECT * FROM gadm2_countries_simple
             WHERE iso = UPPER('{iso}')) as p
        WHERE ST_Intersects(pt.the_geom, p.the_geom)
            AND pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date
        GROUP BY p.iso"""

    ID1 = """
        SELECT p.id_1, p.name_1, count(pt.*) AS value
        FROM modis_forest_change_copy pt,
            (SELECT * FROM gadm2_provinces_simple
             WHERE iso = UPPER('{iso}') AND id_1 = {id1}) as p
        WHERE ST_Intersects(pt.the_geom, p.the_geom)
            AND pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date
        GROUP BY p.id_1, p.name_1
        ORDER BY p.id_1"""

    WDPA = """
        SELECT p.wdpaid, count(pt.*) AS value
        FROM modis_forest_change_copy pt,
            (SELECT * FROM wdpa_all WHERE wdpaid = {wdpaid}) as p
        WHERE ST_Intersects(pt.the_geom, p.the_geom)
            AND pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date
        GROUP BY p.wdpaid
        ORDER BY p.wdpaid"""

    USE = """
        SELECT p.cartodb_id, count(pt.*) AS value
        FROM modis_forest_change_copy pt,
            (SELECT * FROM {use_table} WHERE cartodb_id = {pid}) as p
        WHERE ST_Intersects(pt.the_geom, p.the_geom)
            AND pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date
        GROUP BY p.cartodb_id
        ORDER BY p.cartodb_id"""

    @classmethod
    def download(cls, sql):
        return 'TODO'


def _processResults(action, data):
    if 'rows' in data:
        result = data['rows'][0]
        data.pop('rows')
    else:
        result = dict(value=None)

    data['value'] = result['value']

    return action, data


def execute(args):
    action, data = CartoDbExecutor.execute(args, QuiccSql)
    return _processResults(action, data)
