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

from gfw.v2.subscriptions.handlers import SubscriptionsApi

routes = [
  webapp2.Route(
    r'/v2/subscriptions',
    handler=SubscriptionsApi,
    handler_method='index',
    methods=['GET']
  ),

  webapp2.Route(
    r'/v2/subscriptions',
    handler=SubscriptionsApi,
    handler_method='create',
    methods=['POST']
  ),

  webapp2.Route(
    r'/v2/subscriptions/<subscription_id>',
    handler=SubscriptionsApi,
    handler_method='put',
    methods=['PUT']
  ),

  webapp2.Route(
    r'/v2/subscriptions/<subscription_id>',
    handler=SubscriptionsApi,
    handler_method='delete',
    methods=['DELETE']
  ),

  webapp2.Route(
    r'/v2/subscriptions/<subscription_id>/unsubscribe',
    handler=SubscriptionsApi,
    handler_method='unsubscribe',
    methods=['GET']
  ),

  webapp2.Route(
    r'/v2/subscriptions<:/?.*>',
    handler=SubscriptionsApi,
    methods=['OPTIONS']
  )
]

handlers = webapp2.WSGIApplication(routes, debug=True)
