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

from gfw import common
from gfw.middlewares.cors import CORSRequestHandler
from gfw.geostore.geostore import Geostore

class GeostoreHandler(CORSRequestHandler):
    def get(self, geostore_id):
        geostore = ndb.Key(urlsafe=geostore_id).get()
        self.complete('respond', geostore.to_dict())

    def post(self):
        geostore = Geostore()
        geostore.populate(**self.__get_params())
        geostore.put()

        self.response.set_status(201)
        self.complete('respond', geostore.to_dict())

    def __get_params(self):
        accepted_params = ["geojson"]
        params = json.loads(self.request.body)
        return {k: v for k, v in params.items() if k in accepted_params}

handlers = webapp2.WSGIApplication([
  webapp2.Route(
    r'/geostore/',
    handler=GeostoreHandler,
    handler_method='post',
    methods=['POST']
  ),

  webapp2.Route(
    r'/geostore/<geostore_id>',
    handler=GeostoreHandler,
    handler_method='get',
    methods=['GET']
  )
], debug=common.IS_DEV)
