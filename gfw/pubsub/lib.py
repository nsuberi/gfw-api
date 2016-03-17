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

BASE_PATH = '/map'

ALLOWED_PARAMS = [
    'tab', 'geojson', 'geostore', 'wdpaid', 'begin', 'end', 'threshold',
    'dont_analyze', 'hresolution', 'tour', 'subscribe', 'use', 'useid'
]

BASELAYERS = {
    'alerts/treeloss': 'loss',
    'alerts/treegain': 'forestgain',
    'alerts/sad': 'imazon',
    'alerts/quicc': 'modis',
    'alerts/terra': 'terrailoss',
    'alerts/prodes': 'prodes',
    'alerts/guyra': 'guyra',
    'alerts/glad': 'umd_as_it_happens'
};

def iso(params):
    iso = 'ALL'
    if params.get('iso'):
        iso = params.get('iso')

    if params.get('id1'):
        iso += '-' + str(params.get('id1'))

    return iso

def gfw_map_url(params):
    if not params: return BASE_PATH

    if 'geom' in params:
        params['geojson'] = json.dumps(params['geom'])

    url_params = {k: params[k] for k in ALLOWED_PARAMS if k in params}
    query_string = urllib.urlencode(url_params, doseq=True)

    return BASE_PATH + '/-1/0/0/' + iso(params) + '/grayscale/' + \
        BASELAYERS[params.get('topic') or 'alerts/treeloss'] + \
        '?' + query_string
