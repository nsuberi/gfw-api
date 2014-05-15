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

"""This module supports querying QUICC alerts."""

import json
import logging

from gfw import cdb
from gfw import common
from gfw import sql


API = "%s/forest-change/quicc-alerts{/iso}{/id1}{?period,geojson,use,download}" \
    % common.APP_BASE_URL


META = {
    "description": "Alerts when 40 percent green vegetation cover loss is detected from the previous quarter.",
    "resolution": "5 x 5 kilometers",
    "coverage": "Global except for areas >37 degrees north",
    "timescale": "October 2011 to present",
    "updates": "Quarterly",
    "source": "MODIS",
    "units": "Alerts",
    "name": "QUICC Alerts",
    "id": "quicc-alerts",
    "api_url": API,
}


def _query_args(params):
    """Return prepared query args from supplied API params."""
    args = {}
    filters = []
    select = []
    gadm_filters = []
    group_by = []
    order_by = []

    # National and subnational
    if 'iso' in params and not 'id1' in params:
        select.append('g.iso')
        select.append('count(t.*) AS value')
        gadm_filters.append("iso = upper('%s')" % params['iso'])
        filters.append('ST_Intersects(t.the_geom, g.the_geom)')
        group_by.append('g.iso')
    elif 'iso' in params and 'id1' in params:
        select.append('g.id_1')
        select.append('g.name_1')
        select.append('count(t.*) AS value')
        gadm_filters.append("iso = upper('%s')" % params['iso'])
        gadm_filters.append("id_1 = %s" % params['id1'])
        filters.append('ST_Intersects(t.the_geom, g.the_geom)')
        group_by.append('g.id_1')
        group_by.append('g.name_1')
        order_by.append('g.id_1')

    else:  # Global query
        select.append('count(t.*) AS value')
        if 'geojson' in params:
            filters.append("""ST_INTERSECTS(ST_SetSRID(
                ST_GeomFromGeoJSON('%s'),4326),t.the_geom)""" %
                           params['geojson'])

    # Common filters
    if 'begin' in params:
        filters.append("t.date >= '%s'" % params['begin'])
    if 'end' in params:
        filters.append("t.date <= '%s'" % params['end'])

    # {select}
    args['select'] = ','.join(select)

    # {where}
    if filters:
        args['where'] = 'WHERE ' + ' AND '.join(filters)
    else:
        args['where'] = ''

    # {gadm_where}
    if gadm_filters:
        args['gadm_where'] = 'WHERE ' + ' AND '.join(gadm_filters)
    else:
        args['gadm_where'] = ''

    # {group_by}
    if group_by:
        args['group_by'] = ','.join(group_by)
    else:
        args['group_by'] = ''

    # {order_by}
    if order_by:
        args['order_by'] = 'ORDER BY ' + ','.join(order_by)
    else:
        args['order_by'] = ''

    logging.info(args)
    return args


def _query_response(response, params):
    """Return world response."""
    if response.status_code == 200:
        result = json.loads(response.content)['rows'][0]
        result.update(META)
        result.update(params)
        if 'geojson' in params:
            result['geojson'] = json.loads(params['geojson'])
        return result
    else:
        raise Exception(response.content)


def _download_args(params):
    args = _query_args(params)
    fmt = params.get('format')
    if fmt != 'csv':
        args['select'] = ', the_geom'
    else:
        args['select'] = ''
    args['format'] = fmt
    return args


def _use_args(params):
    args = {}
    if params['use'] == 'logging':
        args['table'] = 'logging_all_merged'
    elif params['use'] == 'mining':
        args['table'] = 'mining_permits_merge'
    elif params['use'] == 'oilpalm':
        args['table'] = 'oil_palm_permits_merge'
    elif params['use'] == 'fiber':
        args['table'] = 'fiber_all_merged'
    args['pid'] = params['use_pid']
    filters = []
    if 'begin' in params:
        filters.append("date >= '%s'" % params['begin'])
    if 'end' in params:
        filters.append("date <= '%s'" % params['end'])
    filters.append('t.cartodb_id = %s' % params['use_pid'])
    filters.append('ST_Intersects(forma.the_geom, t.the_geom)')
    args['where'] = ' AND '.join(filters)
    args['where'] = ' WHERE ' + args['where']
    return args


def query(**params):
    """Query FORMA with supplied params and return result."""
    if 'use' in params:
        return use_query(**params)
    args = _query_args(params)
    if 'iso' in params:
        query = sql.QUICC_ANALYSIS_GADM.format(**args)
    else:
        query = sql.QUICC_ANALYSIS.format(**args)
    response = cdb.execute(query)
    return _query_response(response, params)


def use_query(**params):
    args = _use_args(params)
    query = sql.FORMA_USE.format(**args)
    response = cdb.execute(query)
    return _query_response(response, params)


def download(**params):
    """Return CartoDB download URL for supplied params."""
    args = _download_args(params)
    query = sql.FORMA_DOWNLOAD.format(**args)
    download_args = dict(format=params['format'])
    if 'filename' in params:
        download_args['filename'] = params['filename']
    return cdb.get_url(query, download_args)

