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
from gfw.common import CORSRequestHandler
from engineauth import models
from engineauth.models import User
from engineauth.models import UserProfile
from google.appengine.ext import ndb

from gfw.pubsub.subscription import Subscription

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    }
}

class UserApi(CORSRequestHandler):
    """Handler for user info."""

    def dispatch(self):
        self.user = self.request.user if self.request.user else None
        if self.user is None:
            return self.write_error(401, 'Unauthorised')
        else:
            webapp2.RequestHandler.dispatch(self)

    def get_session(self):
        profile = UserProfile.get_by_id(self.user.auth_ids[0])

        info = profile.user_info['info']
        email = info.get('emails')[0]['value'] if info.get('emails') else None
        user_details = {
            'name': info.get('displayName'),
            'email': email,
            'username': info.get('nickname'),
            'raw': info
        }

        self.complete('respond', user_details)

    def get(self):
        self.complete('respond', self.user.to_dict())

    def post(self):
        self.user.name    = self.request.get('name')
        self.user.email   = self.request.get('email')
        self.user.job     = self.request.get('job')
        self.user.sector  = self.request.get('sector')
        self.user.country = self.request.get('country')
        self.user.gender  = self.request.get('gender')
        self.user.use     = self.request.get('use')
        self.user.signup  = self.request.get('signup')
        self.user.put()

        self.redirect(str(self.request.get('redirect')))

    def subscriptions(self):
        subscriptions = Subscription.query(Subscription.user_id==self.user.key).fetch()
        subscriptions = [s.to_dict() for s in subscriptions]
        self.complete('respond', subscriptions)

routes = [
    webapp2.Route(r'/user/session',
        handler=UserApi,
        handler_method='get_session',
        methods=['GET']),

    webapp2.Route(r'/user',
        handler=UserApi,
        handler_method='post',
        methods=['POST']),

    webapp2.Route(r'/user',
        handler=UserApi,
        handler_method='get',
        methods=['GET']),

    webapp2.Route(r'/user/subscriptions',
        handler=UserApi,
        handler_method='subscriptions',
        methods=['GET']),

]

handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)
