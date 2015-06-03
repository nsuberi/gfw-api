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
        SELECT COUNT(pt.*) AS value
        {additional_select}
        FROM quicc_alerts pt
        WHERE pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date
            AND ST_INTERSECTS(
                ST_SetSRID(ST_GeomFromGeoJSON('{geojson}'), 4326), the_geom)"""

    ISO = """
        SELECT COUNT(pt.*) AS value
        {additional_select}
        FROM quicc_alerts pt,
            (SELECT * FROM gadm2_countries_simple
             WHERE iso = UPPER('{iso}')) as p
        WHERE ST_Intersects(pt.the_geom, p.the_geom)
            AND pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date
        """

    ID1 = """
        SELECT COUNT(pt.*) AS value
        {additional_select}
        FROM quicc_alerts pt,
            (SELECT * FROM gadm2_provinces_simple
             WHERE iso = UPPER('{iso}') AND id_1 = {id1}) as p
        WHERE ST_Intersects(pt.the_geom, p.the_geom)
            AND pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date
        """

    WDPA = """
        SELECT COUNT(pt.*) AS value
        FROM quicc_alerts pt,
            (SELECT * FROM wdpa_protected_areas WHERE wdpaid = {wdpaid}) as p
        WHERE ST_Intersects(pt.the_geom, p.the_geom)
            AND pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date"""

    USE = """
        SELECT COUNT(pt.*) AS value
        FROM quicc_alerts pt,
            (SELECT * FROM {use_table} WHERE cartodb_id = {pid}) as p
        WHERE ST_Intersects(pt.the_geom, p.the_geom)
            AND pt.date >= '{begin}'::date
            AND pt.date <= '{end}'::date"""

    LATEST = """
        SELECT DISTINCT date 
        FROM quicc_alerts
        WHERE date IS NOT NULL
        ORDER BY date DESC
        LIMIT {limit}"""
        
    @classmethod
    def download(cls, sql):
        return ' '.join(
            sql.replace("SELECT COUNT(pt.*) AS value", "SELECT pt.*").split())


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
    action, data = CartoDbExecutor.execute(args, QuiccSql)
    if action == 'redirect' or action == 'error':
        return action, data
    return _processResults(action, data)
