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

from gfw import common
from gfw.middlewares.user import UserAuthMiddleware

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
        self.complete('respond', self.__get_profile().to_dict())

    def put(self):
        profile = self.__get_profile()

        profile.populate(**self.__get_params())
        profile.put()

        self.complete('respond', profile.to_dict())

    def sign_out(self):
        self.request.session.key.delete()
        self.response.set_cookie('_eauth', '')
        self.redirect(self.request.referer)

    def __get_profile(self):
        profile = UserProfile.get_by_id(self.user.auth_ids[0])

        info = profile.user_info['info']
        if not hasattr(profile, 'email'):
            provider_email = info.get('emails')[0]['value'] if info.get('emails') else None
            profile.email = provider_email

        return profile

    def __get_params(self):
        accepted_params = ["name", "email", 'job', 'sector', 'country',
            'state', 'city', 'use', 'sign_up']
        params = json.loads(self.request.body)
        return {k: v for k, v in params.items() if k in accepted_params}


routes = [
    webapp2.Route(r'/user',
        handler=UserApi,
        handler_method='get',
        methods=['GET']),

    webapp2.Route(r'/user/sign_out',
        handler=UserApi,
        handler_method='sign_out',
        methods=['GET']),

    webapp2.Route(r'/user',
        handler=UserApi,
        handler_method='put',
        methods=['PUT', 'POST']),

    webapp2.Route(r'/user',
        handler=UserApi,
        handler_method='options',
        methods=['OPTIONS'])
]

handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)
