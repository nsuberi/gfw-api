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

from gfw.forestchange import forma, quicc, args
from gfw.common import CORSRequestHandler


META = {
    'forma-alerts': forma.META,
    'quicc-alerts': quicc.META,
}


def dispatch(path, args):
    if path == '/forest-change/forma-alerts':
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

    def all(self, dataset):
        """Query dataset"""
        try:
            query_args = args.process(self.args())
            self.complete(query_args)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)

    def iso(self, dataset, iso):
        """Query dataset within supplied country."""
        try:
            raw_args = self.args()

            # Ignore geojson since we're querying by iso
            if 'geojson' in raw_args:
                raw_args.pop('geojson')

            # Pass in path arguments
            raw_args['iso'] = iso

            query_args = args.process(raw_args)
            self.complete(query_args)
        except args.ArgError, e:
            self.write_error(400, e.message)

    def iso1(self, dataset, iso, id1):
        """Query dataset within supplied country and province."""
        try:
            raw_args = self.args()

            # Ignore geojson since we're querying by iso+ad1
            if 'geojson' in raw_args:
                raw_args.pop('geojson')

            # Pass in path arguments
            raw_args['iso'] = iso
            raw_args['id1'] = id1

            query_args = args.process(raw_args)
            self.complete(query_args)
        except args.ArgError, e:
            self.write_error(400, e.message)


DATASETS = ['imazon-sad-alerts', 'forma-alerts', 'quicc-alerts',
            'umd-loss-gain', 'nasa-fires']

ROUTE = r'/forest-change/<dataset:(%s)>' % '|'.join(DATASETS)

handlers = webapp2.WSGIApplication([
    webapp2.Route(
        '/forest-change',
        handler=Handler, handler_method='get'),
    webapp2.Route(
        ROUTE,
        handler=APIHandler, handler_method='all'),
    webapp2.Route(
        ROUTE + r'/<iso:[A-z]{3,3}>',
        handler=APIHandler, handler_method='iso'),
    webapp2.Route(
        ROUTE + r'/<iso:[A-z]{3,3}>/<id1:\d+>',
        handler=APIHandler, handler_method='iso1')
    ],
    debug=True)
