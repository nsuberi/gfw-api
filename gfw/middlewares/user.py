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

import webapp2

from gfw.middlewares.cors import CORSRequestHandler

class UserAuthMiddleware(CORSRequestHandler):
    def dispatch(self):
        route = self.request.route.name
        if (self.routes_without_authorisation is not None) and (route in self.routes_without_authorisation):
            webapp2.RequestHandler.dispatch(self)

        options_request = (self.request.method == "OPTIONS")
        self.user = self.request.user if self.request.user else None
        if not options_request and self.user is None:
            return self.write_error(401, 'Unauthorised')
        else:
            webapp2.RequestHandler.dispatch(self)

class AdminAuthMiddleware(CORSRequestHandler):
    def dispatch(self):
        if self.request.headers.get('X-Appengine-Cron') != None:
            return webapp2.RequestHandler.dispatch(self)

        options_request = (self.request.method == "OPTIONS")
        self.user = self.request.user if self.request.user else None
        is_admin = getattr(self.user, 'admin', False)

        if (not options_request and self.user is None) or (is_admin == False):
            return self.write_error(401, 'Unauthorised')
        else:
            webapp2.RequestHandler.dispatch(self)
