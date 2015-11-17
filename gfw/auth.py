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

config = {
    'webapp2_extras.sessions': {
        'secret_key': 'wIDjEesObzp5nonpRHDzSp40aba7STuqC6ZRY'
    }
}


class UserApi(CORSRequestHandler):
    """Handler for user info."""
    def _send_response(self, data, error=None):
        """Sends supplied result dictionnary as JSON response."""
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept')
        self.response.headers.add_header('charset', 'utf-8')
        self.response.headers["Content-Type"] = "application/json"
        if error:
            self.response.set_status(400)
        if not data:
            self.response.out.write('')
        else:
            self.response.out.write(data)
        if error:
            taskqueue.add(url='/log/error', params=error, queue_name="log")

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
                        self.complete('respond', {'name': name, 'email': email, 'username': username,
                            'raw': info})
                    else:
                        self.complete('respond', {'error': 'No user profile for the current session.'})
                else:
                    self.complete('respond', {'error': 'No user info for the current session.'})
            else:
                self.complete('respond', {'error': 'No cookie assigned yet.'})

        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: Users API (%s)' % name
            monitor.log(self.request.url, msg, error=e,
                        headers=self.request.headers)
    def _get_params(self, body=False):
        if body:
            print self.request.get('name')
        else:
            args = self.request.arguments()
            vals = map(self.request.get, args)
            params = dict(zip(args, vals))
        return params

    def post(self):
        params = self._get_params(body=True)
        try:
            webbrowser.open('http://localhost:5000')
        except Exception, error:
            name = error.__class__.__name__
            trace = traceback.format_exc()
            msg = 'Publish failure: %s: %s' % \
                (name, error)
            monitor.log(self.request.url, msg, error=trace,
                        headers=self.request.headers)
            self._send_error()
    
routes = [
        webapp2.Route(r'/user/session',
            handler=UserApi,
            handler_method='get',
            methods=['GET']),
        webapp2.Route(r'/user/setuser',
            handler=UserApi,
            handler_method='post',
            methods=['POST'])
        ]


handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)
