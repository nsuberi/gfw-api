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

"""This module supports pubsub."""

import json
import webapp2
import monitor
import re
import traceback

from hashlib import md5

from gfw.pubsub.event import Event
from gfw.pubsub.notification import Notification
from gfw.pubsub.subscription import Subscription

from appengine_config import runtime_config
from google.appengine.ext import ndb
from google.appengine.api import mail
from google.appengine.api import taskqueue
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

#
# Handlers
#
class Subscriber(InboundMailHandler):
    def receive(self, message):
        if message.to.find('<') > -1:
            token = message.to.split('<')[1].split('+')[1].split('@')[0]
        else:
            token = message.to.split('+')[1].split('@')[0]
        token = self.request.get('token')
        if Subscription.confirm(token):
          self.response.write('Subscription confirmed!')
        else:
          self.error(404)  


class Confirmer(webapp2.RequestHandler):
    def get(self):
        token = self.request.get('token')
        if Subscription.confirm(token):
            self.response.write('Subscription confirmed!')
        else:
            self.error(404)        


class Publisher(webapp2.RequestHandler):
    def post(self):
        """Publish notifications to all event subscribers."""
        e = ndb.Key(urlsafe=self.request.get('event')).get()

        if not e.multicasted:
            for s in Subscription.get_by_topic(e.topic):
                n = Notification.get(e, s)
                if not n:
                    n = Notification.create(e, s)
                    n.put()

                taskqueue.add(
                    url='/pubsub/notify',
                    queue_name='pubsub-notify',
                    params=dict(notification=n.key.urlsafe()))
        e.multicasted = True
        e.put()


class SubscriptionDump(webapp2.RequestHandler):
    def get(self):
        email = self.request.get('email')
        subs = [x.to_dict(exclude=['created']) for x in Subscription.get_by_email(email)]
        self.response.headers.add_header('charset', 'utf-8')
        self.response.headers["Content-Type"] = "application/json"
        self.response.out.write(json.dumps(subs, sort_keys=True))


#
# Pubsub API: TODO needs refactoring
#
""" BaseApi """
class BaseApi(webapp2.RequestHandler):
    """Base request handler for API."""

    def _send_response(self, data, error=None):
        """Sends supplied result dictionnary as JSON response."""
        self._prep_headers()
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

    def _get_id(self, params):
        whitespace = re.compile(r'\s+')
        params = re.sub(whitespace, '', json.dumps(params, sort_keys=True))
        return '/'.join([self.request.path.lower(), md5(params).hexdigest()])

    def _get_params(self, body=False):
        if body:
            params = json.loads(self.request.body)
        else:
            args = self.request.arguments()
            vals = map(self.request.get, args)
            params = dict(zip(args, vals))
        return params

    def _prep_headers(self):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept'
        )

    def options(self):
        """Options to support CORS requests."""
        self._prep_headers()
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET'


""" PubSubApi """
class PubSubApi(BaseApi):
    
    def subscribe(self):
        try:
            params = self._get_params(body=True)
            topic, email = map(params.get, ['topic', 'email'])
            if Subscription.subscribe(topic, email, params):
                self.response.set_status(201)
                self._send_response(json.dumps(dict(subscribe=True)))
            else:
                self.error(404)  

        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: PubSub API (%s)' % name
            monitor.log(
                self.request.url, 
                msg, 
                error=e,
                headers=self.request.headers
            )


    def unsubscribe(self):
        try:
            params = self._get_params(body=True)
            topic, email = map(params.get, ['topic', 'email'])
            Subscription.unsubscribe(topic, email)
            self._send_response(json.dumps(dict(unsubscribe=True)))

        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: PubSub API (%s)' % name
            monitor.log(
                self.request.url, 
                msg, 
                error=e,        
                headers=self.request.headers
            )


    def publish(self):
        try:
            params = self._get_params(body=True)
            topic = params['topic']
            Event.publish(topic,params)
            self._send_response(json.dumps(dict(publish=True)))

        except Exception, error:
            name = error.__class__.__name__
            trace = traceback.format_exc()
            msg = 'Publish failure: %s: %s' % (name, error)
            monitor.log(
                self.request.url, 
                msg, 
                error=trace,
                headers=self.request.headers
            )
            self._send_error()




