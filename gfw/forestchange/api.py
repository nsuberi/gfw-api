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

"""This module is the entry point for the forest change API.

Supported data sources include UMD, FORMA, IMAZON, QUICC, and Nasa Fires.
"""

import datetime
import json
import logging
import sys
import webapp2

from google.appengine.api import memcache

from gfw.forestchange import forma, quicc
from gfw.common import CORSRequestHandler


META = {
    # 'umd-loss-gain'=None,
    'forma-alerts': forma.META,
    'quicc-alerts': quicc.META,
    # 'imazon-sad-alerts'=None,
    # 'nasa-fires'=None
}


class Handler(CORSRequestHandler):
    """Default handler that returns META json."""
    def get(self):
        self.write(json.dumps(META))


class FORMAHandler(CORSRequestHandler):
    """Handler for FORMA requests."""

    def _handle_exception(self, e):
        """Common handler for exceptions."""
        logging.exception(e)
        if e.message == 'need more than 1 value to unpack':
            msg = '{"error": ["Invalid period parameter"]}'
        elif e.message == 'period':
            msg = '{"error": ["The period parameter is required"]}'
        elif e.message == 'geojson':
            msg = '{"error": ["The geojson parameter is required"]}'
        elif e.message == "invalid period (begin > end)":
            msg = '{"error": ["The period parameter begin > end"]}'
        elif e.message == 'No JSON object could be decoded':
            msg = '{"error": ["Invalid geojson parameter"]}'
        elif e.message == 'Unknown use':
            msg = '{"error": ["Invalid use parameter (unknown use name)"]}'
        elif e.message.startswith('invalid literal for int() with base 10'):
            msg = '{"error": ["Invalid use param (polygon id not a number)"]}'
        elif e.message.startswith('Unsupported geojson type'):
            msg = '{"error": ["%s"]}' % e.message
        else:
            # TODO monitor
            msg = e.message
        self.write_error(400, msg)

    def handle_request(self, params, dataset):
        """Common handler for a request with supplied params dictionary."""
        fmt = params.get('format', 'json')
        if dataset == 'forma-alerts':
            module = forma
        elif dataset == 'quicc-alerts':
            module = quicc
        # Handle analysis request
        if fmt == 'json':
            rid = self.get_id(params)
            result = memcache.get(rid)
            if not result or 'bust' in params:
                result = module.query(**params)
                memcache.set(key=rid, value=result)
            self.write(json.dumps(result, sort_keys=True))
        # Handle download request
        else:
            self.redirect(forma.download(**params))

    def get_params(self):
        """Return prepared params from supplied GET request args."""
        args = self.args()
        if not args:
            return {}
        params = {}
        period = args.get('period', ',')
        begin, end = period.split(',')
        if begin and end:
            f = datetime.datetime.strptime
            b, e = f(begin, '%Y-%m-%d'), f(end, '%Y-%m-%d')
            if b > e:
                raise Exception("invalid period (begin > end)")
            params['begin'] = begin
            params['end'] = end
        if 'geojson' in args:
            params['geojson'] = args['geojson']
            geom = json.loads(params['geojson'])
            if geom['type'] != 'Polygon' and geom['type'] != 'MultiPolygon':
                raise Exception('Unsupported geojson type %s' % geom['type'])
        if 'download' in args:
            filename, fmt = args['download'].split('.')
            params['format'] = fmt
            params['filename'] = filename
        if 'use' in args:
            name, pid = args['use'].split(',')
            if not name in ['logging', 'mining', 'oilpalm', 'fiber']:
                raise Exception('Unknown use')
            int(pid)
            params['use'] = name
            params['use_pid'] = pid
        return params

    def world(self, dataset):
        """Query FORMA globally."""
        try:
            params = self.get_params()
            self.handle_request(params, dataset)
        except (Exception, ValueError) as e:
            self._handle_exception(e)

    def iso(self, dataset, iso):
        """Query FORMA by country iso."""
        try:
            params = self.get_params()
            if 'geojson' in params:
                params.pop('geojson')
            params['iso'] = iso
            self.handle_request(params, dataset)
        except (Exception, ValueError) as e:
            self._handle_exception(e)

    def iso1(self, dataset, iso, id1):
        """Query FORMA by country province."""
        try:
            params = self.get_params()
            if 'geojson' in params:
                params.pop('geojson')
            params['iso'] = iso
            params['id1'] = id1
            self.handle_request(params, dataset)
        except (Exception, ValueError) as e:
            self._handle_exception(e)


DATASETS = ['imazon-sad-alerts', 'forma-alerts', 'quicc-alerts',
            'umd-loss-gain', 'nasa-fires']

ROUTE = r'/forest-change/<dataset:(%s)>' % '|'.join(DATASETS)

handlers = webapp2.WSGIApplication([
    webapp2.Route(
        '/forest-change',
        handler=Handler, handler_method='get'),
    webapp2.Route(
        ROUTE,
        handler=FORMAHandler, handler_method='world'),
    webapp2.Route(
        ROUTE + r'/<iso:[A-z]{3,3}>',  # country
        handler=FORMAHandler, handler_method='iso'),
    webapp2.Route(
        ROUTE + r'/<iso:[A-z]{3,3}>/<id1:\d+>',  # country+state
        handler=FORMAHandler, handler_method='iso1')],
    debug=True)
