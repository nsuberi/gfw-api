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
import re
import webapp2

from gfw.countries import countries
from gfw.countries import args
from gfw.common import CORSRequestHandler
from gfw.common import APP_BASE_URL

FORMA_API = '%s/forma-alerts' % APP_BASE_URL

META = {

}


def _classify_request(path):
    """Classify request based on supplied path."""
    if re.match(r'^countries$', path):
        return 'index'
    elif re.match(r'^countries/[A-z]{3,3}$', path):
        return 'iso'
    elif re.match(r'^countries/[A-z]{3,3}/\d+$', path):
        return 'id1'


class Handler(CORSRequestHandler):
    """API handler for countries."""

    def post(self):
        self.get()

    def get(self):
        try:
            path = self.request.path.strip("/")

            rtype = _classify_request(path)
            # Unsupported dataset or reqest type
            if not rtype:
                self.error(404)
                return

            # Return API meta
            if path == 'countries':
                action, data = self._action_data()
            else:   
                path_args = args.process_path(path, rtype)
                action, data = self._action_data(path_args)

            self.complete(action, data)

        except Exception, e:
            logging.exception(e)
            self.write_error(400, e.message)
            self.write(json.dumps(META, sort_keys=True))


    def _action_data(self,path_args={'index': True}):
        query_args = args.process(self.args(only=['dev', 'bust', 'thresh']))
        params = dict(query_args, **path_args)
        rid = self.get_id(params)
        return self.get_or_execute(params, countries, rid)


handlers = webapp2.WSGIApplication([(r'/countries.*', Handler)], debug=True)
