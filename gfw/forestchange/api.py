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


def handle_forma_world(args):
    begin, end = args['period'].split(',')
    geojson = args['geojson']
    return forma.query_world(begin=begin, end=end, geojson=geojson)


def handle_forma_iso(args):
    pass


def handle_forma_iso1(args):
    pass


class FORMAHandler(CORSRequestHandler):
    """Handler for API requests."""

    def world(self):
        try:
            args = self.args()
            if not args:
                result = forma.META
            else:
                begin, end = args['period'].split(',')
                geojson = args['geojson']
                result = forma.query_world(
                    begin=begin, end=end, geojson=geojson)
            self.write(json.dumps(result, sort_keys=True))
        except Exception, e:
            logging.exception(e)
            if e.message == 'need more than 1 value to unpack':
                msg = '{"error": ["Invalid period parameter"]}'
            else:
                msg = e.message
            self.write(msg)

    def iso(self, dataid, iso):
        logging.info('dataid=%s, iso=%s' % (dataid, iso))

    def iso1(self, dataid, iso, id1):
        logging.info('dataid=%s, iso=%s, id1=%s' % (dataid, iso, id1))


FOREST_CHANGE_ROUTE = r'/forest-change/forma'

handlers = webapp2.WSGIApplication([

    # FORMA routes
    webapp2.Route(
        r'/forest-change/forma',  # World
        handler=FORMAHandler, handler_method='world'),
    webapp2.Route(
        r'/forest-change/forma/<iso:[A-z]{3,3}>',  # Country
        handler=FORMAHandler, handler_method='iso'),
    webapp2.Route(
        r'/forest-change/forma//<iso:[A-z]{3,3}>/<id1:\d+>',  # Level 1
        handler=FORMAHandler, handler_method='iso1')],


    debug=True)
