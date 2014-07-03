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

"""This module supports accessing countries data."""

import json

from gfw import cdb
from gfw.forestchange import umd


class CountrySql(object):

    TOPO_JSON = """
        SELECT the_geom
        FROM forest_cov_glob_v3
        WHERE country_code = UPPER('{iso}')
        UNION
        SELECT the_geom
        FROM ne_50m_admin_0_countries
        WHERE adm0_a3 = UPPER('{iso}')"""

    SUBNAT_BOUNDS = """
        SELECT cartodb_id, iso, id_1, name_1, bounds
        FROM gadm_1_all
        WHERE iso = UPPER('{iso}')
        ORDER BY id_1 asc"""

    TENURE = """
        SELECT tenure_government, tenure_owned, tenure_owned_individuals,
            tenure_reserved, GREATEST(tenure_government, tenure_owned,
            tenure_owned_individuals, tenure_owned_individuals,
            tenure_reserved) AS max
        FROM gfw2_countries
        WHERE iso = UPPER('{iso}')"""

    FORESTS = """
        SELECT unnest(array['forest_regenerated', 'forest_primary',
               'forest_planted']) AS type, unnest(array[COALESCE(
               forest_regenerated, 0), COALESCE(forest_primary, 0), COALESCE(
               forest_planted, 0)]) AS percent
        FROM gfw2_countries
        WHERE iso = UPPER('{iso}')"""

    FORMA = """
        SELECT date_trunc('month', date) AS date, COUNT(*) AS alerts
        FROM forma_api
        WHERE iso = UPPER('{iso}')
        GROUP BY date_trunc('month', date)
        ORDER BY date_trunc('month', date) ASC"""

    BOUNDS = """
        SELECT bounds
        FROM country_mask
        WHERE code = UPPER('{iso}')"""


def _handler(response):
    if response.status_code == 200:
        data = json.loads(response.content)
        if 'rows' in data:
            return data['rows']
        else:
            return data
    else:
        raise Exception(response.content)


def _getTopoJson(args):
    query = CountrySql.TOPO_JSON.format(**args)

    rows = _handler(
        cdb.execute(query, params=dict(format='topojson')))
    return dict(topojson=rows)


def _processSubnatRow(x):
    x['bounds'] = json.loads(x['bounds'])
    return x


def _getSubnatBounds(args):
    query = CountrySql.SUBNAT_BOUNDS.format(**args)

    rows = _handler(cdb.execute(query))
    results = map(_processSubnatRow, rows)
    return dict(subnat_bounds=results)


def _getForma(args):
    query = CountrySql.FORMA.format(**args)

    return dict(forma=_handler(cdb.execute(query)))


def _getForests(args):
    query = CountrySql.FORESTS.format(**args)

    return dict(forests=_handler(cdb.execute(query)))


def _getTenure(args):
    query = CountrySql.TENURE.format(**args)

    return dict(tenure=_handler(cdb.execute(query)))


def _getBounds(args):
    query = CountrySql.BOUNDS.format(**args)

    return dict(bounds=json.loads(_handler(cdb.execute(query))[0]['bounds']))


def _getUmd(args):
    action, data = umd.execute(args)

    return dict(umd=data['years'])


def execute(args):
    result = dict(params=args)

    result.update(_getTopoJson(args))
    result.update(_getSubnatBounds(args))
    result.update(_getForma(args))
    result.update(_getForests(args))
    result.update(_getTenure(args))
    result.update(_getBounds(args))
    result.update(_getUmd(args))

    return 'respond', result
