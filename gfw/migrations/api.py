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

import json
import webapp2
import logging
import base64

from google.appengine.ext import ndb
from google.appengine.datastore.datastore_query import Cursor

from gfw import common
from gfw.middlewares.cors import CORSRequestHandler

from gfw.geostore.geostore import Geostore
from gfw.models.subscription import Subscription
from gfw.user.gfw_user import GFWUser

from appengine_config import runtime_config as config

PER_PAGE = 10

def user_to_dict(u):
    profile = u.get_profile().to_dict();
    d = u.to_dict();
    d['user_id'] = u.key.id()
    d['profile'] = profile;
    return d

class BasicAuthRequestHandler(CORSRequestHandler):
    def dispatch(self):
        basic_auth = self.request.headers.get('Authorization')

        if not basic_auth:
            logging.debug("Request does not carry auth.")
            self.response.set_status(401, 'Unauthorised')
            self.response.headers['WWW-Authenticate'] = 'Basic realm="secure"'
            return self.response.out.write('Unauthorised')

        try:
            user_info = base64.decodestring(basic_auth[6:])
            username, password = user_info.split(':')

            if username == config.get('migration_user') and \
                    password == config.get('migration_password'):
                return webapp2.RequestHandler.dispatch(self)
            else:
                return self.write_error(401, 'Unauthorised')
        except Exception as e:
            print "error"
            print e
            return self.write_error(401, 'Unauthorised')

class MigrationsHandler(BasicAuthRequestHandler):
    def geostore(self):
        cursor_id = self.args().get('cursor')
        cursor = Cursor(urlsafe=cursor_id)
        geostores, next_cursor, more = Geostore.query().fetch_page(PER_PAGE, start_cursor=cursor)

        to_dict = lambda g: g.to_dict()
        geostores_as_dicts = map(to_dict, geostores)

        if more:
            next_cursor = next_cursor.urlsafe()
        else:
            next_cursor = None

        self.complete('respond', {
            "geostore": geostores_as_dicts,
            "cursor": next_cursor
        })

    def subscriptions(self):
        cursor_id = self.args().get('cursor')
        cursor = Cursor(urlsafe=cursor_id)
        subscriptions, next_cursor, more = Subscription.query().fetch_page(PER_PAGE, start_cursor=cursor)

        to_dict = lambda g: g.to_dict()
        subscriptions_as_dicts = map(to_dict, subscriptions)

        if more:
            next_cursor = next_cursor.urlsafe()
        else:
            next_cursor = None

        self.complete('respond', {
            "subscriptions": subscriptions_as_dicts,
            "cursor": next_cursor
        })

    def users(self):
        cursor_id = self.args().get('cursor')
        cursor = Cursor(urlsafe=cursor_id)
        users, next_cursor, more = GFWUser.query().fetch_page(PER_PAGE, start_cursor=cursor)

        users_as_dicts = map(user_to_dict, users)

        if more:
            next_cursor = next_cursor.urlsafe()
        else:
            next_cursor = None

        self.complete('respond', {
            "users": users_as_dicts,
            "cursor": next_cursor
        })


handlers = webapp2.WSGIApplication([
  webapp2.Route(
    r'/migrations/geostore',
    handler=MigrationsHandler,
    handler_method='geostore'
  ),

  webapp2.Route(
    r'/migrations/subscriptions',
    handler=MigrationsHandler,
    handler_method='subscriptions'
  ),

  webapp2.Route(
    r'/migrations/users',
    handler=MigrationsHandler,
    handler_method='users'
  )
], debug=True)
