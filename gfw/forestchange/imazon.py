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

    # ISO same as WORLD since imazon only in Brazil

    ISO = """
        SELECT data_type,
            sum(ST_Area(i.the_geom_webmercator)/(100*100)) AS value
        FROM imazon_monthly i
        WHERE i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY data_type
        """

    ID1 = """
        SELECT i.data_type as disturbance,
            SUM(ST_Area(ST_Intersection(
                i.the_geom_webmercator,
                p.the_geom_webmercator))/(100*100)) AS value
        FROM imazon_monthly i,
            (SELECT *
                FROM gadm2 WHERE iso = UPPER('{iso}') AND id_1 = {id1}) as p
        WHERE i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY i.data_type"""

    WDPA = """
        SELECT i.data_type,
            SUM(ST_Area(ST_Intersection(
                i.the_geom_webmercator,
                p.the_geom_webmercator))/(100*100)) AS value
        FROM (SELECT * FROM wdpa_all WHERE wdpaid = {wdpaid}) p,
            imazon_monthly i
        WHERE i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY i.data_type"""

    USE = """
        SELECT i.data_type,
            SUM(ST_Area(ST_Intersection(
                i.the_geom_webmercator,
                p.the_geom_webmercator))/(100*100)) AS value
        FROM {use_table} p, imazon_monthly i
        WHERE p.cartodb_id = {pid}
            AND i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY i.data_type"""

    @classmethod
    def download(cls, sql):
        return 'TODO'


NO_DATA = [dict(disturbance='defor', value=None),
           dict(disturbance='degrad', value=None)]


def _processResults(action, data, args):

    # Only have data for Brazil
    if 'iso' in args and args['iso'].lower() != 'bra':
        result = NO_DATA
    elif 'rows' in data:
        result = data['rows']
    else:
        result = NO_DATA

    if 'rows' in data:
        data.pop('rows')

    data['value'] = result

    return action, data


def execute(args):
    action, data = CartoDbExecutor.execute(args, ImazonSql)
    return _processResults(action, data, args)
