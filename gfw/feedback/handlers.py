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

import webapp2
import json
import urllib

from gfw.middlewares.cors import CORSRequestHandler

from appengine_config import runtime_config

from google.appengine.api import taskqueue

class FeedbackApi(CORSRequestHandler):
    """Handler for user info."""

    def post(self):
        encoded_email = self.__get_params()['email']
        email = urllib.unquote(encoded_email).decode('utf8') 

        taskqueue.add(url='/feedback/tasks/tester',
            queue_name='feedback-tester',
            params={'email': email})

        self.complete('respond', {})

    def __get_params(self):
        accepted_params = ["email"]
        params = json.loads(self.request.body)
        return {k: v for k, v in params.items() if k in accepted_params}
