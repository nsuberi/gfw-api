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

import datetime
import json
import logging
import webapp2
import os

from google.appengine.api import taskqueue
from google.appengine.ext import ndb
from google.appengine.ext.webapp import template

from gfw.lib.urls import map_url
from gfw.middlewares.user import AdminAuthMiddleware
from gfw.models.event import Event
from gfw.models.topic import Topic
from gfw.models.subscription import Subscription

def get_subscription_emails(event):
    subscriptions = Subscription.query(Subscription.topic ==
            event.topic, Subscription.confirmed == True)
    return [s.email for s in subscriptions.iter()]

def get_subscriptions(event):
    subscriptions = Subscription.query(Subscription.topic ==
            event.topic, Subscription.confirmed == True)

    alerts = []
    for subscription in subscriptions.iter():
        try:
            topic_result = subscription.run_analysis(event.begin, event.end)

            if (topic_result.is_zero() == False):
                alerts.append({
                    'count': topic_result.formatted_value(),
                    'subscription': subscription
                })
        except Exception:
            pass

    return alerts

def send_subscriptions(event):
    taskqueue.add(url='/manage/pubsub/tasks/publish_subscriptions',
        queue_name='pubsub-publish-subs',
        params=dict(event=event.key.urlsafe()))

def set_url(event, alert):
    url_params = alert['subscription'].params
    url_params['begin'] = event.begin
    url_params['end'] = event.end
    url_params['fit_to_geom'] = 'true'
    url_params['tab'] = 'analysis-tab'
    alert['subscription_url'] = map_url(alert['subscription'].params)
    return alert

def set_url_factory(event):
    return lambda alert: set_url(event, alert)

class PubSubManagementApi(AdminAuthMiddleware):
    def automatic(self):
        params = self.args()

        if 'topic' in params:
            selected_topic = params['topic']
        else:
            self.write_error(400, 'Bad Request')

        previous_event = Event.latest_for_topic(selected_topic)
        event = Event(topic=selected_topic)

        if previous_event == None:
            self.write_error(400, 'Bad Request')

        event.begin = previous_event.end
        event.end = datetime.datetime.now()

        if 'send' in params:
            event.put()
            send_subscriptions(event)
            return self.complete('respond', {})

        self.write_error(400, 'Bad Request')

    def post(self):
        params = self.args()
        if 'topic' in params:
            selected_topic = params['topic']
        else:
            selected_topic = Topic.all()[0].id

        previous_event = Event.latest_for_topic(selected_topic)
        event = Event(topic=selected_topic)
        if previous_event != None:
            event.begin = previous_event.end

        if 'begin' in params:
            event.begin = datetime.datetime.strptime(params['begin'], '%Y-%m-%d')

        if 'end' in params:
            event.end = datetime.datetime.strptime(params['end'], '%Y-%m-%d')

        if 'send' in params:
            event.put()
            send_subscriptions(event)
            self.redirect('/manage/pubsub?success=true')

        alerts = []
        if 'preview' in params:
            alerts = get_subscriptions(event)
            alerts = map(set_url_factory(event), alerts)

        emails = []
        if 'preview_emails' in params:
            emails = get_subscription_emails(event)

        template_values = {
            'topics': Topic.all(),
            'selected_topic': selected_topic,
            'begin_date': event.begin.strftime('%Y-%m-%d'),
            'end_date': event.end.strftime('%Y-%m-%d'),
            'alerts': alerts,
            'emails': emails,
            'preview': 'preview' in params,
            'preview_emails': 'preview_emails' in params,
            'success': 'success' in params
        }

        template_path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(template_path, template_values))
