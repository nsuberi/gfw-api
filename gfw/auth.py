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

"""This module contains request handlers for user authentication."""

import webapp2
import webbrowser
import monitor
import json
import cgi

from gfw import common
from gfw.common import UserAuthMiddleware

from engineauth import models
from engineauth.models import User
from engineauth.models import UserProfile

from google.appengine.ext import ndb

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    }
}

class UserApi(UserAuthMiddleware):
    """Handler for user info."""

    def get(self):
        profile = UserProfile.get_by_id(self.user.auth_ids[0])

        info = profile.user_info['info']
        if not hasattr(profile, 'email'):
            provider_email = info.get('emails')[0]['value'] if info.get('emails') else None
            profile.email = provider_email

        self.complete('respond', profile.to_dict())

    def post(self):
        profile = UserProfile.get_by_id(self.user.auth_ids[0])

        profile.name    = self.request.get('name')
        profile.email   = self.request.get('email')
        profile.job     = self.request.get('job')
        profile.sector  = self.request.get('sector')
        profile.country = self.request.get('country')
        profile.gender  = self.request.get('gender')
        profile.use     = self.request.get('use')
        profile.signup  = self.request.get('signup')
        profile.put()

        self.redirect(str(self.request.get('redirect')))

routes = [
    webapp2.Route(r'/user',
        handler=UserApi,
        methods=['POST', 'GET'])
]

handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)
