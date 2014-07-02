# Global Forest Watch API
# Copyright (C) 2013 World Resource Institute
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

"""This module supports accessing UMD data."""

from gfw.forestchange.common import CartoDbExecutor, Sql, classify_query


class UmdSql(Sql):

    ISO = """
        SELECT iso, country, year, thresh, extent, extent_perc, loss,
               loss_perc, gain, gain_perc
        FROM umd_nat
        WHERE iso = UPPER('{iso}')
              AND thresh = {thresh}
        ORDER BY year"""

    ID1 = """
        SELECT iso, country, region, year, thresh, extent, extent_perc, loss,
               loss_perc, gain, gain_perc
        FROM umd_subnat
        WHERE iso = UPPER('{iso}')
              AND thresh = {thresh}
              AND id1 = {id1}
        ORDER BY iso, country, region, thresh, year"""

    @classmethod
    def iso(cls, params, args):
        params['iso'] = args['iso']
        params['thresh'] = args['thresh']
        query_type, params = cls.get_query_type(params, args)
        if query_type == 'download':
            return cls.ISO.format(**params)
        else:
            return cls.ISO.format(**params)


def _executeIso(args):
    action, data = CartoDbExecutor.execute(args, UmdSql)
    rows = data['rows']
    data.pop('rows')
    data['years'] = rows
    return action, data


def execute(args):
    query_type = classify_query(args)

    if query_type == 'iso' or query_type == 'id1':
        return _executeIso(args)

    # TODO: Query new EE assets
