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
import re
import logging
import webapp2

from google.appengine.api import memcache
from appengine_config import runtime_config

from hashlib import md5
from urlparse import urlparse

ALLOWED_DOMAINS = ['globalforestwatch.org', 'staging.globalforestwatch.org', 'localhost:5000']

class CORSRequestHandler(webapp2.RequestHandler):

    def _set_origin_header(self):
        if 'Origin' in self.request.headers:
            origin = self.request.headers['Origin']
            domain = urlparse(origin).netloc

            if domain in ALLOWED_DOMAINS:
                self.response.headers.add_header("Access-Control-Allow-Origin", origin)
                self.response.headers.add_header("Access-Control-Allow-Credentials", "true")
                return

        self.response.headers.add_header("Access-Control-Allow-Origin", "*")

    def options(self):
        """Options to support CORS requests."""
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = \
            'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET'

    def write(self, data):
        """Sends supplied result dictionnary as JSON response."""

        self._set_origin_header()
        self.response.headers.add_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept')
        self.response.headers.add_header('charset', 'utf-8')
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(str(data))

    def write_error(self, status, data):
        """Sends supplied result dictionnary as JSON response."""

        self._set_origin_header()
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept')
        self.response.headers.add_header('charset', 'utf-8')
        self.response.headers["Content-Type"] = "application/json"
        self.response.set_status(status, message=str(data))
        self.response.out.write(str(data))

    @classmethod
    def get_or_execute(cls, args, target, rid):
        if 'bust' in args:
            memcache.delete(rid)
            result = target.execute(args)
        else:
            result = memcache.get(rid)
            if not result:
                result = target.execute(args)
                try:
                    memcache.set(key=rid, value=result)
                except Exception as e:
                    logging.exception(e)
        action, data = result
        return action, data

    def args(self, only=[]):
        raw = {}
        if not self.request.arguments():
            if self.request.body:
                raw = json.loads(self.request.body)
        else:
            args = self.request.arguments()
            vals = map(self.request.get, args)
            raw = dict(zip(args, vals))

        result = {}
        for key, val in raw.iteritems():
            if only and key in only:
                result[key] = val
            else:
                result[key] = val

        return result

    def complete(self, action, data):
        if action == 'respond':
            self.write(json.dumps(data, sort_keys=True))
        elif action == 'redirect':
            self.redirect(data)
        elif action == 'error':
            self.write_error(400, data.get('message') or data )
        else:
            self.write_error(400, 'Unknown action %s' % action)

    def get_id(self, params):
        whitespace = re.compile(r'\s+')
        params = re.sub(whitespace, '', json.dumps(params, sort_keys=True))
        return '/'.join([self.request.path.lower(), md5(params).hexdigest()])

#
# SHARED CONSTANTS/TEMPLATES
#
APP_VERSION = runtime_config.get('APP_VERSION')
APP_BASE_URL = runtime_config.get('APP_BASE_URL')
IS_DEV = runtime_config.get('IS_DEV')
CONTENT_TYPES = {
    'shp': 'application/octet-stream',
    'kml': 'application/vnd.google-earth.kmz',
    'svg': 'image/svg+xml',
    'csv': 'application/csv',
    'geojson': 'application/json',
    'json': 'application/json'
}
GCS_URL_TMPL = 'http://storage.googleapis.com/gfw-apis-analysis%s.%s'


#
# Helper Methods
#
def get_params_hash(params):
    return md5(json.dumps(params, sort_keys=True)).hexdigest()


def get_cartodb_format(gfw_media_type):
    """Return CartoDB format for supplied GFW custom media type."""
    tokens = gfw_media_type.split('.')
    if len(tokens) == 2:
        return 'json'
    else:
        return tokens[2].split('+')[0]
