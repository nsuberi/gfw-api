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

    ISO = """
        SELECT p.iso,
            SUM(ST_Area(i.the_geom_webmercator)/(100*100)) AS total_ha
        FROM imazon_clean2 i,
            (SELECT * FROM gadm2_countries WHERE iso = UPPER('{iso}')) AS p
        WHERE ST_Intersection(i.the_geom, p.the_geom)
            AND i.date >= '{begin}'::date
            AND i.date <= '{end}'::date
        GROUP BY p.iso"""

    ID1 = """
        """

    WDPA = """
        """

    USE = """
        """


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
