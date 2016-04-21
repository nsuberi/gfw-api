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

import json
import webapp2

from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

from gfw import common
from gfw.middlewares.cors import CORSRequestHandler
from gfw.geostore.geostore import Geostore

class GeostoreHandler(CORSRequestHandler):
    def index(self):
        per_page = 50
        cursor_id = self.args().get('cursor')
        cursor = Cursor(urlsafe=cursor_id)
        geostores, next_cursor, more = Geostore.query().fetch_page(per_page, start_cursor=cursor)

        to_dict = lambda g: g.to_dict()
        geostores_as_dicts = map(to_dict, geostores)

        if more:
            next_cursor = next_cursor.urlsafe()
        else:
            next_cursor = None

        self.complete('respond', {
            "geostore": geostores_as_dicts,
            "cursor": next_cursor
        })

    def get(self, geostore_id):
        geostore = ndb.Key(urlsafe=geostore_id).get()
        self.complete('respond', geostore.to_dict())

    def post(self):
        body = self.request.body
        geostore = Geostore.create_from_request_body(body)

        self.response.set_status(201)
        self.complete('respond', geostore.to_dict())

handlers = webapp2.WSGIApplication([
  webapp2.Route(
    r'/geostore/',
    handler=GeostoreHandler,
    handler_method='post',
    methods=['POST']
  ),

  webapp2.Route(
    r'/geostore/all',
    handler=GeostoreHandler,
    handler_method='index',
    methods=['GET']
  ),

  webapp2.Route(
    r'/geostore/<geostore_id>',
    handler=GeostoreHandler,
    handler_method='get',
    methods=['GET']
  )
], debug=common.IS_DEV)
