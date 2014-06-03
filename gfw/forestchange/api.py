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

from google.appengine.api import memcache

from gfw.forestchange import forma, args
from gfw.common import CORSRequestHandler


META = {
    'forma-alerts': forma.META,
    # 'quicc-alerts': quicc.META,
}


def dispatch(path, args):
    if '/forest-change/forma-alerts' in path:
        target = forma
    return target.execute(args)


class Handler(CORSRequestHandler):
    """Default handler that returns META json."""
    def get(self):
        self.write(json.dumps(META))


class APIHandler(CORSRequestHandler):

    def complete(self, args):
        if 'bust' in args:
            result = dispatch(self.request.path, args)
        else:
            rid = self.get_id(args)
            result = memcache.get(rid)
            if not result:
                result = dispatch(self.request.path, args)
                memcache.set(key=rid, value=result)
        action, data = result
        if action == 'respond':
            self.write(json.dumps(data, sort_keys=True))
        elif action == 'redirect':
            self.redirect(data)
        elif action == 'error':
            self.write_error(400, data.message)
        else:
            self.write_error(400, 'Unknown action %s' % action)


class FormaAllHandler(APIHandler):
    """Handler for /forest-change/forma-alerts"""

    PARAMS = ['period', 'download', 'geojson', 'dev', 'bust']

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            query_args = args.process(raw_args)
            self.complete(query_args)
        except args.ArgError, e:
            logging.exception(e)

    def post(self):
        self.get()


class FormaIsoHandler(APIHandler):
    """"Handler for /forest-change/forma-alerts/admin/{iso}"""

    PARAMS = ['period', 'download', 'dev', 'bust']

    @classmethod
    def iso_from_path(cls, path):
        """Return iso code from supplied request path."""
        return path.split('/')[4]

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            raw_args['iso'] = self.iso_from_path(self.request.path)
            query_args = args.process(raw_args)
            self.complete(query_args)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FormaIsoId1Handler(APIHandler):
    """"Handler for /forest-change/forma-alerts/admin/{iso}/{id1}"""

    PARAMS = ['period', 'download', 'dev', 'bust']

    @classmethod
    def iso_id1_from_path(cls, path):
        """Return iso code and id1 from supplied request path."""
        return path.split('/')[4], path.split('/')[5]

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            iso, id1 = self.iso_id1_from_path(self.request.path)
            raw_args['iso'] = iso
            raw_args['id1'] = id1
            query_args = args.process(raw_args)
            self.complete(query_args)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FormaWdpaHandler(APIHandler):
    """"Handler for /forest-change/forma-alerts/admin/{iso}/{id1}"""

    PARAMS = ['period', 'download', 'dev', 'bust']

    @classmethod
    def wdpaid_from_path(cls, path):
        """Return wdpaid from supplied request path."""
        return path.split('/')[4]

    def get(self):
        try:
            raw_args = self.args(only=['period', 'download'])
            raw_args['wdpaid'] = self.wdpaid_from_path(self.request.path)
            query_args = args.process(raw_args)
            self.complete(query_args)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


handlers = webapp2.WSGIApplication([
    (r'/forest-change', Handler),

    # FORMA endpoints
    (r'/forest-change/forma-alerts', APIHandler),
    (r'/forest-change/forma-alerts/admin/[A-z]{3,3}', FormaIsoHandler),
    (r'/forest-change/forma-alerts/admin/[A-z]{3,3}/\d+', FormaIsoId1Handler),
    (r'/forest-change/forma-alerts/wdpa/\d+', FormaWdpaHandler),
    ],
    debug=True)
