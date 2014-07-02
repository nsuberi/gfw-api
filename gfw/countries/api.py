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

"""This module is the entry point for the forest change API."""

import json
import logging
import webapp2

from gfw.countries import countries
from gfw.common import CORSRequestHandler
from gfw.common import APP_BASE_URL

FORMA_API = '%s/forma-alerts' % APP_BASE_URL

META = {
    'countries': {
    }
}


# Maps query type to accepted query params
PARAMS = {
    'forma-alerts': {
        'all': ['period', 'download', 'geojson', 'dev', 'bust'],
        'iso': ['period', 'download', 'dev', 'bust'],
        'id1': ['period', 'download', 'dev', 'bust'],
        'wpda': ['period', 'download', 'dev', 'bust'],
        'use': ['period', 'download', 'dev', 'bust'],
    },
    'umd-loss-gain': {
        'iso': ['download', 'dev', 'bust', 'thresh'],  # TODO: thresh
        'id1': ['download', 'dev', 'bust', 'thresh'],  # TODO: thresh
    }
}


def _isoFromPath(path):
    """Return ISO code from supplied request path.

    Path format: /countries/{iso}"""
    tokens = path.split('/')
    return tokens[2] if len(tokens) >= 1 else None


class Handler(CORSRequestHandler):
    """API handler for countries."""

    def post(self):
        self.get()

    def get(self):
        try:
            path = self.request.path

            # Return API meta
            if path == '/countries':
                self.complete('respond', META)
                return

            iso = _isoFromPath(path)

            # Unsupported dataset or reqest type
            if not iso:
                self.error(404)
                return

            # Handle request
            params = dict(iso=iso)
            bust = self.request.get('bust')
            rid = self.get_id(params)
            if bust:
                params['bust'] = 1
            action, data = self.get_or_execute(params, countries, rid)
            self.complete(action, data)
        except Exception, e:
            logging.exception(e)
            self.write_error(400, e.message)
            self.write(json.dumps(META, sort_keys=True))


handlers = webapp2.WSGIApplication([
    (r'/countries.*', Handler)],
    debug=True)
