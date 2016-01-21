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


import webapp2
import urlparse
import json

from gfw import common
from gfw.middlewares.cors import CORSRequestHandler

from google.appengine.api import urlfetch

METADATA_URL = "http://54.88.79.102/gfw-sync/metadata/"

def metadata_url(param):
    return urlparse.urljoin(METADATA_URL, param.split('/')[-1])

IGNORE_HEADERS = frozenset([
    "set-cookie",
    "expires",
    "cache-control",
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade"
])

class MetadataApi(CORSRequestHandler):
    def get(self, param):
        url = metadata_url(param)
        response = urlfetch.fetch(url)

        for key, value in response.headers.iteritems():
            adjusted_key = key.lower()
            if adjusted_key not in IGNORE_HEADERS:
                self.response.headers.add_header(adjusted_key, value)

        try:
            self.complete('respond', json.loads(response.content))
        except Exception as e:
            self.complete('respond', {})


routes = [
    webapp2.Route(
        r'/metadata<:/?.*>',
        handler=MetadataApi,
        handler_method='get',
        methods=['GET'])
]

handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)
