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

from gfw import cdb
from gfw import sql


META = {
    "description": "Alerts when 40% green vegetation cover loss from the previous quarter.",
    "resolution": "5 x 5 kilometers",
    "coverage": "Global except for areas >37 degrees north",
    "timescale": "October 2011 to present",
    "updates": "Quarterly",
    "source": "MODIS",
    "units": "Alerts",
    "name": "QUICC Alertsv"
}


def _query_args(params):
    """Return prepared query args from supplied API params."""
    args = {}
    filters = []
    if 'geojson' in params:
        filters.append("""ST_INTERSECTS(ST_SetSRID(
            ST_GeomFromGeoJSON('%s'),4326),the_geom)""" % params['geojson'])
    if 'iso' in params:
        filters.append("iso = upper('%s')" % params['iso'])
    if 'id1' in params:
        filters.append("id_1 = '%s'" % params['id1'])
    if 'begin' in params:
        filters.append("date >= '%s'" % params['begin'])
    if 'end' in params:
        filters.append("date <= '%s'" % params['end'])
    args['where'] = ' AND '.join(filters)
    if args['where']:
        args['where'] = ' WHERE ' + args['where']
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
    query = sql.FORMA_ANALYSIS.format(**args)
    response = cdb.execute(query)
    return _query_response(response, params)


















import json
from gfw import cdb

ANALYSIS = """SELECT count(*) AS total {select_geom}
FROM modis_forest_change_copy m, world_countries c
WHERE m.date = '{date}'::date
      AND m.country = c.name
      AND c.iso3 = upper('{iso}')
GROUP BY c.the_geom"""

ANALYSIS_GEOM = """SELECT count(*) AS total {select_geom}
FROM modis_forest_change_copy m, world_countries c
WHERE ST_Intersects(m.the_geom,ST_SetSRID(ST_GeomFromGeoJSON('{geom}'),4326))
      AND m.date = '{date}'::date
GROUP BY c.the_geom"""

def query(**params):


def download(params):
    params['select_geom'] = ', c.the_geom'
    geom = params.get('geom')
    if geom:
        query = ANALYSIS_GEOM.format(**params)
        params['filename'] = 'gfw_quicc_{date}'.format(**params)
    else:
        query = ANALYSIS.format(**params)
        params['filename'] = 'gfw_quicc_{iso}_{date}'.format(**params)
    return cdb.get_url(query, params)


def analyze(params):
    params['select_geom'] = ''
    if 'iso' in params:
        params['iso'] = params['iso'].upper()
    geom = params.get('geom')
    if geom:
        query = ANALYSIS_GEOM.format(**params)
    else:
        query = ANALYSIS.format(**params)
    return cdb.execute(query)


def parse_analysis(content):
    rows = json.loads(content)['rows']
    if rows:
        result = rows[0]
    else:
        result = dict(total=0)
    return result
