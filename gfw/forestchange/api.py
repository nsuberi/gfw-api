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

"""This module is the entry point for forest change API.

Supported data sources include UMD, FORMA, IMAZON, QUICC, and Nasa Fires.
"""

import json
import logging
import webapp2

from gfw.forestchange import forma
from gfw.common import CORSRequestHandler


class FORMAHandler(CORSRequestHandler):
    """Handler for FORMA requests."""

    def world_params(self):
        """Return prepared params from supplied GET request args."""
        args = self.args()
        if not args:
            return {}
        params = {}
        period = args.get('period')
        if period:
            begin, end = period.split(',')
            if begin:
                params['begin'] = begin
            if end:
                params['end'] = end
        if 'geojson' in args:
            params['geojson'] = args['geojson']
        return params

    def world(self):
        """Query world for FORMA alerts with supplied period and geojson."""
        try:
            params = self.world_params()
            result = forma.query(**params)
            self.write(json.dumps(result, sort_keys=True))
        except Exception, e:
            logging.exception(e)
            if e.message == 'need more than 1 value to unpack':
                msg = '{"error": ["Invalid period parameter"]}'
            elif e.message == 'period':
                msg = '{"error": ["The period parameter is required"]}'
            elif e.message == 'geojson':
                msg = '{"error": ["The geojson parameter is required"]}'
            else:
                # TODO monitor
                msg = e.message
            self.write(msg)

    def iso(self, iso):
        try:
            params = self.world_params()
            if 'geojson' in params:
                params.pop('geojson')
            params['iso'] = iso
            result = forma.query(**params)
            self.write(json.dumps(result, sort_keys=True))
        except Exception, e:
            logging.exception(e)
            self.write(e.message)

    def iso1(self, iso, id1):
        try:
            params = self.world_params()
            if 'geojson' in params:
                params.pop('geojson')
            params['iso'] = iso
            params['id1'] = id1
            result = forma.query(**params)
            self.write(json.dumps(result, sort_keys=True))
        except Exception, e:
            logging.exception(e)
            self.write(e.message)

FOREST_CHANGE_ROUTE = r'/forest-change/forma'

handlers = webapp2.WSGIApplication([

    # FORMA routes
    webapp2.Route(
        r'/forest-change/forma',  # world
        handler=FORMAHandler, handler_method='world'),
    webapp2.Route(
        r'/forest-change/forma/<iso:[A-z]{3,3}>',  # country
        handler=FORMAHandler, handler_method='iso'),
    webapp2.Route(
        r'/forest-change/forma/<iso:[A-z]{3,3}>/<id1:\d+>',  # country+state
        handler=FORMAHandler, handler_method='iso1')],


    debug=True)
