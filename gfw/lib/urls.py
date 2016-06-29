# Global Forest Watch API
# Copyright (C) 2015 World Resource Institute
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

import urllib
import json

from gfw.models.topic import Topic

from appengine_config import runtime_config

BASE_PATH = '/map'
BASE_URL = runtime_config.get('GFW_BASE_URL')

ALLOWED_PARAMS = [
    'tab', 'geojson', 'geostore', 'wdpaid', 'begin', 'end', 'threshold',
    'dont_analyze', 'hresolution', 'tour', 'subscribe', 'use', 'useid',
    'fit_to_geom'
]

def iso(params):
    iso = 'ALL'
    if params.get('iso'):
        iso = params.get('iso')

    if params.get('id1'):
        iso += '-' + str(params.get('id1'))

    return iso

def map_url(params, utm={}):
    if not params: return BASE_PATH

    if 'begin' in params:
        params['begin'] = params['begin'].strftime('%Y-%m-%d')
    if 'end' in params:
        params['end'] = params['end'].strftime('%Y-%m-%d')

    if 'geostore' in params and params['geostore'] is None:
        del params['geostore']

    if 'geostore' not in params and 'geom' in params:
        geojson = json.dumps(params['geom'])
        if len(geojson) <= 1000:
            params['geojson'] = geojson

    if 'topic' in params:
        topic = Topic.get_by_id(params['topic'])
    else:
        topic = Topic.all()[0]

    baselayer = topic.baselayer

    url_params = {k: params[k] for k in ALLOWED_PARAMS if k in params}
    url_params = dict(url_params.items() + utm.items())

    query_string = urllib.urlencode(url_params, doseq=True)

    return BASE_URL + BASE_PATH + '/-1/0/0/' + iso(params) + '/grayscale/' + \
        baselayer + '?' + query_string
