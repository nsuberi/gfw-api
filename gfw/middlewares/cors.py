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

import json
import copy
import re
import logging
import webapp2
import datetime;
from hashlib import md5
from urlparse import urlparse

from google.appengine.api import memcache
from google.appengine.ext import ndb

from gfw.common import ALLOWED_DOMAINS

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

    def options(self, *args, **kwargs):
        """Options to support CORS requests."""

        self._set_origin_header()
        self.response.headers['Access-Control-Allow-Headers'] = \
            'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET, PUT, DELETE'

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
            if only:
                if key in only:
                    result[key] = val
            else:
                result[key] = val

        return result

    def json_serial(self, obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        if isinstance(obj, ndb.Key):
            return obj.id()

    def complete(self, action, data):
        if action == 'respond':
            self.write(json.dumps(data, sort_keys=True, default=self.json_serial))
        elif action == 'redirect':
            self.redirect(data)
        elif action == 'error':
            self.write_error(400, data.get('message') or data )
        else:
            self.write_error(400, 'Unknown action %s' % action)

    def get_id(self, params):
        normalized_params = copy.copy(params)
        if 'bust' in normalized_params: normalized_params.pop('bust')
        normalized_params = json.dumps(normalized_params, sort_keys=True, default=self.json_serial)
        normalized_params = re.sub(re.compile(r'\s+'), '', normalized_params)

        return md5(self.request.host + self.request.path + normalized_params).hexdigest()

