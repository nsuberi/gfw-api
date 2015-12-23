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

class Userdata(ndb.Model):
    name     = ndb.StringProperty()
    email    = ndb.StringProperty()
    job      = ndb.StringProperty()
    sector   = ndb.StringProperty()
    country  = ndb.StringProperty()
    gender   = ndb.StringProperty()
    use      = ndb.StringProperty()
    signup   = ndb.StringProperty()
    user_id  = ndb.StringProperty()

class UserApi(CORSRequestHandler):
    """Handler for user info."""

    def get(self):
        # Currently Supports Twitter Auth:
        try:
            value = self.request.cookies.get('_eauth')
            if value:
                session = models.Session.get_by_value(value)
                if session.user_id:
                    self.user = User.get_by_id(int(session.user_id))
                    self.profile = UserProfile.get_by_id(self.user.auth_ids[-1])
                    if self.profile:
                        info = self.profile.user_info['info']
                        name = info['displayName']
                        if hasattr(info, 'emails'):
                            email = info['emails'][0]['value']
                        else:
                            email = None;
                        if hasattr(info, 'username'):
                            username = info['nickname']
                        else:
                            username = None;

                        self.complete('respond', {'name': name, 'email': email, 'username': username, 'raw': info})
                    else:
                        self.complete('error', {'error': 'No user profile for the current session.'}, True)
                else:
                    self.complete('error', {'error': 'No user info for the current session.'}, True)
            else:
                self.complete('error', {'error': 'No authentication cookie provided.'}, True)

        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: Users API (%s)' % name
            monitor.log(self.request.url, msg, error=e,
                        headers=self.request.headers)

    def post(self):
        try:
            value = self.request.cookies.get('_eauth')
            if value:
                session = models.Session.get_by_value(value)
                if session.user_id:
                    userdata = Userdata(
                                    name    = self.request.get('name')      or "*nonamee*",
                                    email   = self.request.get('email')     or "*noemaile*",
                                    job     = self.request.get('job')       or "*nojobe*",
                                    sector  = self.request.get('sector')    or "*nosectore*",
                                    country = self.request.get('country')   or "*nocountrye*",
                                    gender  = self.request.get('gender')    or "*nogendere*",
                                    use     = self.request.get('use')       or "*noemaile*",
                                    signup  = self.request.get('signup')    or "*nosignupe*",
                                    user_id = session.user_id)
                userdata.put()
                self.redirect(str(self.request.get('redirect')))
        except Exception, error:
            self.redirect('http://www.globalforestwatch.com')

    def subscriptions(self):
        value = self.request.cookies.get('_eauth')
        if value:
            session = models.Session.get_by_value(value)
            if session.user_id:
                subscriptions = Subscription.query(Subscription.user_id==session.user_id).fetch()
                subscriptions = [s.to_dict() for s in subscriptions]
                self.complete('respond', subscriptions)
                return

        self.write_error(401, 'Unauthorised')

    def getuser(self):
        print 'hola'
        value = self.request.cookies.get('_eauth')
        if value:
            session = models.Session.get_by_value(value)
            if session.user_id:
                user = json.dumps([p.to_dict() for p in  Userdata.query(Userdata.user_id==session.user_id).fetch() ])
                self.complete('respond', user)
                return

        self.write_error(401, 'Unauthorised')


routes = [
    webapp2.Route(r'/user/subscriptions',
        handler=UserApi,
        handler_method='subscriptions',
        methods=['GET']),
    webapp2.Route(r'/user/session',
        handler=UserApi,
        handler_method='get',
        methods=['GET']),
    webapp2.Route(r'/user/setuser',
        handler=UserApi,
        handler_method='post',
        methods=['POST']),
    webapp2.Route(r'/user/getuser',
        handler=UserApi,
        handler_method='getuser',
        methods=['GET'])
]

handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)
