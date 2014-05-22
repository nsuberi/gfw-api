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

"""This module provides functions for dealing with FORMA data."""

import json
import logging

from gfw import cdb
from gfw import common
from gfw import sql


API = "%s/forest-change/forma-alerts{/iso}{/id1}{?period,geojson,use,download}" \
    % common.APP_BASE_URL


META = {
    "description": "Alerts where forest disturbances have likely occurred.",
    "resolution": "500 x 500 meters",
    "coverage": "Humid tropical forest biome",
    "timescale": "January 2006 to present",
    "updates": "16 day",
    "source": "MODIS",
    "units": "Alerts",
    "name": "FORMA",
    "api_url": API,
    "id": "forma-alerts"
}


def _query_args(params):
    """Return prepared query args from supplied API params."""
    args = {}
    filters = []
    gadm_filters = []
    print 'hi'
    if 'iso' in params and not 'id1' in params:
        filters.append("iso = upper('%s')" % params['iso'])
    if 'iso' in params and 'id1' in params:
        gadm_filters.append("id_1 = %s" % params['id1'])
        gadm_filters.append("iso = upper('%s')" % params['iso'])

    if 'geojson' in params:
        filters.append("""ST_INTERSECTS(ST_SetSRID(
            ST_GeomFromGeoJSON('%s'),4326),the_geom)""" % params['geojson'])

    if 'begin' in params:
        filters.append("date >= '%s'" % params['begin'])
    if 'end' in params:
        filters.append("date <= '%s'" % params['end'])

    args['where'] = ' AND '.join(filters)
    if args['where']:
        args['where'] = ' WHERE ' + args['where']

    if gadm_filters:
        args['gadm_where'] = ' AND '.join(gadm_filters)

    return args


def _query_response(response, params, query):
    """Return world response."""
    if response.status_code == 200:
        result = json.loads(response.content)['rows'][0]
        result.update(META)
        result.update(params)
        if 'geojson' in params:
            result['geojson'] = json.loads(params['geojson'])
        if 'dev' in params:
            result['dev'] = {'sql': query}
        return result
    else:
        logging.info(query)
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
    if 'id1' in params:
        query = sql.FORMA_ANALYSIS_GADM.format(**args)
    else:
        query = sql.FORMA_ANALYSIS.format(**args)
    response = cdb.execute(query)
    return _query_response(response, params, query)


def use_query(**params):
    args = _use_args(params)
    query = sql.FORMA_USE.format(**args)
    response = cdb.execute(query)
    return _query_response(response, params, query)


def download(**params):
    """Return CartoDB download URL for supplied params."""
    args = _download_args(params)
    query = sql.FORMA_DOWNLOAD.format(**args)
    download_args = dict(format=params['format'])
    if 'filename' in params:
        download_args['filename'] = params['filename']
    return cdb.get_url(query, download_args)


def classify_query(args):
    if 'iso' in args and not 'id1' in args:
        return 'country'
    elif 'iso' in args and 'id1' in args:
        return 'id1'
    elif 'use' in args:
        return 'concessions'
    else:
        return 'world'


def execute(args):
    try:
        query = sql.FormaSql.process(args)
        response = cdb.execute(query)
        return 'respond', _query_response(response, args, query)
    except sql.SqlError, e:
        return 'error', e
