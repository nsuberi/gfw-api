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

"""This module contains request handlers for the Global Forest Watch API."""

import webapp2


""" ROUTES """

routes = [
  
  # pubsub.Publisher
  webapp2.Route(r'/pubsub/publish', 
                handler=pubsub.Publisher,
                handler_method='post',
                methods=['POST']),
  webapp2.Route(r'/pubsub/confirm',
                handler=pubsub.Confirmer,
                handler_method='get',
                methods=['GET']),
  webapp2.Route(r'/pubsub/notify',
                handler=pubsub.GFWNotify,
                handler_method='post',
                methods=['POST']),
  webapp2.Route(r'/pubsub/dump',
                handler=pubsub.SubscriptionDump,
                handler_method='get',
                methods=['GET']),

  # PubSubApi
  webapp2.Route(r'/subscribe', 
                handler=PubSubApi,
                handler_method='subscribe',
                methods=['POST']),
  webapp2.Route(r'/unsubscribe', 
                handler=PubSubApi,
                handler_method='unsubscribe',
                methods=['POST']),
  webapp2.Route(r'/publish', 
                handler=PubSubApi,
                handler_method='publish',
                methods=['POST']),

  # StoriesApi
  webapp2.Route(r'/stories/new',
                handler=StoriesApi,
                handler_method='create',
                methods=['POST']),
  webapp2.Route(r'/stories',
                handler=StoriesApi,
                handler_method='list'),
  webapp2.Route(r'/stories/<id:\d+>',
                handler=StoriesApi,
                handler_method='get'),
  webapp2.Route(r'/stories/email',
                handler=StoriesApi,
                handler_method='_send_new_story_emails',
                methods=['POST']),
  # Other
  webapp2.Route(r'/subout',
                handler=SubHandler,
                handler_method='get',
                methods=['GET']),

]


handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)