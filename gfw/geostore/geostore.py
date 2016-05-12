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

from appengine_config import runtime_config
from google.appengine.ext import ndb

CHUNK_SIZE = 500000

class Geostore(ndb.Model):
    geojson = ndb.TextProperty()
    next_id = ndb.KeyProperty()

    kind = 'Geostore'

    """ Instance Methods """

    def next_chunk(self):
        next_chunk = self.next_id.get()

    def get_combined_geojson(self):
        geojson = self.geojson
        next_id = self.next_id
        while next_id is not None:
            next_chunk = next_id.get()
            geojson += next_chunk.geojson
            next_id = next_chunk.next_id

        return geojson

    def to_dict(self):
        try:
            result = super(Geostore, self).to_dict()
            result['id'] = self.key.urlsafe()
            result['geojson'] = json.loads(self.get_combined_geojson())
            return result
        except Exception as e:
            return None

    @classmethod
    def create_from_request_body(cls, body):
        body_length = len(body)
        number_of_chunks = body_length / CHUNK_SIZE

        first_chunk = current_chunk = Geostore()
        current_chunk.geojson = body[0:CHUNK_SIZE]
        current_chunk.put()
        for chunk_index in range(1, number_of_chunks+1):
            new_chunk = Geostore()

            start_index = chunk_index * CHUNK_SIZE
            end_index   = (chunk_index + 1) * CHUNK_SIZE
            new_chunk.geojson = body[start_index:end_index]
            new_chunk.put()

            current_chunk.next_id = new_chunk.key
            current_chunk.put()
            current_chunk = new_chunk

        return first_chunk
