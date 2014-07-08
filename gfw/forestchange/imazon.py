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

"""This module supports acessing IMAZON data."""

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql


class ImazonSql(Sql):

    WORLD = """
        SELECT data_type,
            sum(ST_Area(i.the_geom_webmercator)/(100*100)) AS value
        FROM imazon_monthly i
        WHERE i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY data_type"""

    ISO = """
        SELECT p.iso, i.data_type,
            SUM(ST_Area(ST_Intersection(
                    i.the_geom_webmercator,
                    p.the_geom_webmercator))/(100*100)) AS value
        FROM imazon_monthly i,
            (SELECT * FROM gadm2_countries WHERE iso = UPPER('{iso}')) as p
        WHERE i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY p.iso, i.data_type
        """

    ID1 = """
        SELECT p.iso, p.id_1, p.name_1, i.data_type,
            SUM(ST_Area(ST_Intersection(
                i.the_geom_webmercator,
                p.the_geom_webmercator))/(100*100)) AS value
        FROM imazon_monthly i,
            (SELECT *
                FROM gadm2 WHERE iso = UPPER('{iso}') AND id_1 = {id1}) as p
        WHERE i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY p.iso, p.id_1, p.name_1, i.data_type"""

    WDPA = """
        SELECT p.cartodb_id, i.data_type,
            SUM(ST_Area(ST_Intersection(
                i.the_geom_webmercator,
                p.the_geom_webmercator))/(100*100)) AS value
        FROM (SELECT * FROM wdpa_all WHERE wdpaid = {wdpaid}) p,
            imazon_monthly i
        WHERE i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY p.cartodb_id, i.data_type"""

    USE = """
        SELECT p.cartodb_id, i.data_type,
            SUM(ST_Area(ST_Intersection(
                i.the_geom_webmercator,
                p.the_geom_webmercator))/(100*100)) AS value
        FROM {use_table} p, imazon_monthly i
        WHERE p.cartodb_id = {pid}
            AND i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY p.cartodb_id, i.data_type"""


def _processResults(action, data):
    if 'rows' in data:
        result = data['rows'][0]
        data.pop('rows')
    else:
        result = dict(value=None)

    data['value'] = result['value']

    return action, data


def execute(args):
    action, data = CartoDbExecutor.execute(args, ImazonSql)
    return _processResults(action, data)
