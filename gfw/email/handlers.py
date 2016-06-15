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
import webapp2

from gfw.models.email import Email
from gfw.middlewares.cors import CORSRequestHandler

class EmailApi(CORSRequestHandler):
    def send(self):
        params = self.__get_params()

        email = Email()
        email.user_email = params['contact-email']
        email.message = params['contact-message']
        email.topic = params['contact-topic']
        email.opt_in = (params['contact-signup'] == "true")
        email.put()

        if email:
            token = email.key.urlsafe()
            self.response.set_status(201)
            self.complete('respond', {"key": token})
        else:
            self.write_error(400, 'Bad Request')

    def __get_params(self):
        return json.loads(self.request.body)
