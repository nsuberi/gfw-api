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
import json

from gfw.middlewares.user import UserAuthMiddleware

from appengine_config import runtime_config

from engineauth.models import User
from engineauth.models import UserProfile

from google.appengine.ext import ndb

class UserApi(UserAuthMiddleware):
    """Handler for user info."""

    def get(self):
        profile = self.__get_profile()

        if not hasattr(profile, 'is_new'):
            profile.is_new = True
            profile.put()

        profile = profile.to_dict()
        profile['id'] = self.user.key.id()

        self.complete('respond', profile)

    def put(self):
        profile = self.__get_profile()

        profile.populate(**self.__get_params())
        profile.put()
        self.user.put()

        self.complete('respond', profile.to_dict())

    def sign_out(self):
        self.request.session.key.delete()
        self.response.delete_cookie('_eauth')

        if 'my_gfw' not in self.request.referer:
            self.redirect(self.request.referer)
        else:
            self.redirect(runtime_config['GFW_BASE_URL'])

    def __get_profile(self):
        profile = UserProfile.get_by_id(self.user.auth_ids[0])

        info = profile.user_info['info']
        if not hasattr(profile, 'email'):
            provider_email = info.get('emails')[0]['value'] if info.get('emails') else None
            profile.email = provider_email

        return profile

    def __get_params(self):
        accepted_params = ["name", "email", 'job', 'sector', 'country',
            'state', 'city', 'use', 'sign_up', 'is_new']
        params = json.loads(self.request.body)
        return {k: v for k, v in params.items() if k in accepted_params}
