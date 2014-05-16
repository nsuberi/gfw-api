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

"""This module supports common functions."""

import json
import os
import re
import webapp2

from hashlib import md5


class CORSRequestHandler(webapp2.RequestHandler):

    def options(self, dataset):
        """Options to support CORS requests."""
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = \
            'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET'

    def write(self, data):
        """Sends supplied result dictionnary as JSON response."""
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept')
        self.response.headers.add_header('charset', 'utf-8')
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(str(data))

    def write_error(self, status, data):
        """Sends supplied result dictionnary as JSON response."""
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept')
        self.response.headers.add_header('charset', 'utf-8')
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(status, message=str(data))
        self.response.out.write(str(data))

    def args(self, only=[]):
        if not self.request.arguments():
            if self.request.body:
                return json.loads(self.request.body)
        else:
            args = self.request.arguments()
            vals = map(self.request.get, args)
            return dict(zip(args, vals))

    def get_id(self, params):
        whitespace = re.compile(r'\s+')
        params = re.sub(whitespace, '', json.dumps(params, sort_keys=True))
        return '/'.join([self.request.path.lower(), md5(params).hexdigest()])


CONTENT_TYPES = {
    'shp': 'application/octet-stream',
    'kml': 'application/vnd.google-earth.kmz',
    'svg': 'image/svg+xml',
    'csv': 'application/csv',
    'geojson': 'application/json',
    'json': 'application/json'
}


GCS_URL_TMPL = 'http://storage.googleapis.com/gfw-apis-analysis%s.%s'

IS_DEV = 'Development' in os.environ.get('SERVER_SOFTWARE', 'Development')
APP_VERSION = os.environ.get('CURRENT_VERSION_ID', 'dev')
if '.' in APP_VERSION:
    APP_VERSION = APP_VERSION.split('.')[0]


if IS_DEV:
    APP_BASE_URL = 'http://%s.localhost:8080' % APP_VERSION
else:
    APP_BASE_URL = 'http://%s.gfw-apis.appspot.com' % APP_VERSION


def get_params_hash(params):
    return md5(json.dumps(params, sort_keys=True)).hexdigest()


def get_cartodb_format(gfw_media_type):
    """Return CartoDB format for supplied GFW custom media type."""
    tokens = gfw_media_type.split('.')
    if len(tokens) == 2:
        return 'json'
    else:
        return tokens[2].split('+')[0]
