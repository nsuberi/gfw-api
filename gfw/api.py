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

import base64
import hashlib
import json
import random
import re
import os
import copy
import webapp2
import monitor
import logging
import traceback

from gfw import common
from gfw import countries
from gfw import pubsub
from gfw import wdpa
from appengine_config import runtime_config
from hashlib import md5
from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.ext import ndb


class Entry(ndb.Model):
    value = ndb.TextProperty()


# Countries API route
COUNTRY_ROUTE = r'/countries'

# WPDA site API route
WDPA = r'/wdpa/sites'


class WdpaApi(BaseApi):
    def site(self):
        try:
            params = self._get_params()
            rid = self._get_id(params)
            entry = Entry.get_by_id(rid)
            if not entry or params.get('bust') or runtime_config.get('IS_DEV'):
                site = wdpa.get_site(params)
                if site:
                    entry = Entry(id=rid, value=json.dumps(site))
                    entry.put()
            self._send_response(entry.value if entry else None)
        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: WPDA API (%s)' % name
            monitor.log(self.request.url, msg, error=e,
                        headers=self.request.headers)


class CountryApi(BaseApi):
    """Handler for countries."""

    def get(self):
        try:
            params = self._get_params()
            rid = self._get_id(params)
            if 'interval' not in params:
                params['interval'] = '12 MONTHS'
            entry = Entry.get_by_id(rid)
            if not entry or params.get('bust') or runtime_config.get('IS_DEV'):
                result = countries.get(params)
                if result:
                    entry = Entry(id=rid, value=json.dumps(result))
                    entry.put()
            self._send_response(entry.value if entry else None)
        except Exception, error:
            name = error.__class__.__name__
            trace = traceback.format_exc()
            msg = 'Publish failure: %s: %s' % \
                (name, error)
            monitor.log(self.request.url, msg, error=trace,
                        headers=self.request.headers)


class PubSubApi(BaseApi):

    def subscribe(self):
        try:
            params = self._get_params(body=True)
            pubsub.subscribe(params)
            self.response.set_status(201)
            self._send_response(json.dumps(dict(subscribe=True)))
        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: PubSub API (%s)' % name
            monitor.log(self.request.url, msg, error=e,
                        headers=self.request.headers)

    def unsubscribe(self):
        try:
            params = self._get_params(body=True)
            pubsub.unsubscribe(params)
            self._send_response(json.dumps(dict(unsubscribe=True)))
        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: PubSub API (%s)' % name
            monitor.log(self.request.url, msg, error=e,
                        headers=self.request.headers)

    def publish(self):
        params = self._get_params(body=True)
        try:
            pubsub.publish(params)
            self._send_response(json.dumps(dict(publish=True)))
        except Exception, error:
            name = error.__class__.__name__
            trace = traceback.format_exc()
            msg = 'Publish failure: %s: %s' % \
                (name, error)
            monitor.log(self.request.url, msg, error=trace,
                        headers=self.request.headers)
            self._send_error()


routes = [
    webapp2.Route(COUNTRY_ROUTE, handler=CountryApi,
                  handler_method='get'),
    webapp2.Route(r'/subout', handler=SubHandler,
                  handler_method='get'),
    webapp2.Route(WDPA, handler=WdpaApi,
                  handler_method='site'),
    webapp2.Route(r'/pubsub/publish', handler=pubsub.Publisher,
                  handler_method='post',
                  methods=['POST']),
    webapp2.Route(r'/pubsub/confirm', handler=pubsub.Confirmer,
                  handler_method='get',
                  methods=['GET']),
    webapp2.Route(r'/pubsub/notify', handler=pubsub.Notify,
                  handler_method='post',
                  methods=['POST']),
    webapp2.Route(r'/pubsub/dump', handler=pubsub.SubscriptionDump,
                  handler_method='get',
                  methods=['GET']),
    webapp2.Route(r'/subscribe', handler=PubSubApi,
                  handler_method='subscribe',
                  methods=['POST']),
    webapp2.Route(r'/unsubscribe', handler=PubSubApi,
                  handler_method='unsubscribe',
                  methods=['POST']),
    webapp2.Route(r'/publish', handler=PubSubApi,
                  handler_method='publish',
                  methods=['POST'])
]

handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)
