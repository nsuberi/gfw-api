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

"""Unit tests for gfw.pubsub"""

from test import common

import unittest
import webapp2
import webtest

from datetime import datetime

from gfw.pubsub import api


class SubscribeTest(common.BaseTest):

    def setUp(self):
        super(SubscribeTest, self).setUp()
        app = webapp2.WSGIApplication(
            [(r'/pubsub/sub', api.SubscribeHandler)])
        self.api = webtest.TestApp(app)

    def _test_response(self, response):
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.normal_body, '"{\\"success\\": true}"')
        self.assertEqual(response.content_type, 'application/json')

    def _test_confirmation_email_sent(self, ns=''):
        messages = self.mail_stub.get_sent_messages(to='t@wri.org')
        self.assertEqual(1, len(messages))
        self.assertEqual('t@wri.org', messages[0].to)
        # Test that subscription key.urlsafe in confirmation email:
        sub = api.Subscription.query(namespace=ns).fetch(1)[0]
        self.assertIn(sub.key.urlsafe(), messages[0].body.payload)

    def _test_subscription_model(self, ns=''):
        subs = api.Subscription.query(namespace=ns).fetch(2)
        self.assertEqual(1, len(subs))
        sub = subs[0]
        self.assertEqual(ns, sub.key.namespace())
        self.assertEqual('t@wri.org', sub.email)
        self.assertEqual('alerts/forma', sub.topic)
        self.assertEqual(True, sub.new)
        self.assertEqual(False, sub.confirmed)

    def testSubscribe(self):
        response = self.api.get(
            '/pubsub/sub?email=t@wri.org&topic=alerts/forma')
        self._test_response(response)
        self._test_confirmation_email_sent()
        self._test_subscription_model()

    def testSubscribeTest(self):
        response = self.api.get(
            '/pubsub/sub?email=t@wri.org&topic=alerts/forma&namespace=test')
        self._test_response(response)
        self._test_confirmation_email_sent(ns='test')
        self._test_subscription_model(ns='test')

    def testSubscribeJson(self):
        params = dict(topic='alerts/forma', email='t@wri.org')
        response = self.api.post('/pubsub/sub', params)
        self._test_response(response)
        self._test_confirmation_email_sent()
        self._test_subscription_model()


class SubscribeConfirmTest(common.BaseTest):

    def setUp(self):
        super(SubscribeConfirmTest, self).setUp()
        app = webapp2.WSGIApplication(
            [(r'/pubsub/sub-confirm', api.SubscribeConfirmHandler)])
        self.api = webtest.TestApp(app)

    def testSubcribeConfirm(self):
        sub = api.Subscription(topic='alerts/forma', email='t@wri.org')
        sub.put()
        self.assertEqual(False, sub.confirmed)
        url = '/pubsub/sub-confirm?token=%s' % sub.key.urlsafe()
        response = self.api.get(url)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(
            response.normal_body, '"{\\"status\\": \\"confirmed\\"}"')
        self.assertEqual(response.content_type, 'application/json')
        sub = api.Subscription.query().fetch(1)[0]
        self.assertEqual(True, sub.confirmed)

    def testSubcribeConfirmTest(self):
        ns = 'test'
        sub = api.Subscription(
            namespace=ns, topic='alerts/forma', email='t@wri.org')
        sub.put()
        self.assertEqual(False, sub.confirmed)
        url = '/pubsub/sub-confirm?token=%s' % sub.key.urlsafe()
        response = self.api.get(url)
        self.assertEqual(response.status_int, 200)
        self.assertEqual(
            response.normal_body, '"{\\"status\\": \\"confirmed\\"}"')
        self.assertEqual(response.content_type, 'application/json')
        sub = api.Subscription.query(namespace=ns).fetch(1)[0]
        self.assertEqual(True, sub.confirmed)


class PublishTest(common.BaseTest):

    def setUp(self):
        super(PublishTest, self).setUp()
        app = webapp2.WSGIApplication(
            [(r'/pubsub/pub', api.PublishHandler)])
        self.api = webtest.TestApp(app)

    def _test_response(self, response):
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.normal_body, '"{\\"success\\": true}"')
        self.assertEqual(response.content_type, 'application/json')

    def testPublish(self):
        response = self.api.get('/pubsub/pub?topic=alerts/forma')
        self._test_response(response)
        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, 'pubsub-pub-multicast')


class MulticastTest(common.BaseTest):

    def setUp(self):
        super(MulticastTest, self).setUp()
        app = webapp2.WSGIApplication(
            [(r'/pubsub/pub-multicast', api.MulticastHandler)])
        self.api = webtest.TestApp(app)

    def _test_response(self, response):
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.normal_body, '"{\\"success\\": true}"')
        self.assertEqual(response.content_type, 'application/json')

    def testPublish(self):
        topic = 'alerts/forma'
        s = api.Subscription(topic=topic, email='foo', confirmed=True)
        s.put()
        event = api.Event(topic=topic)
        event.put()
        params = dict(topic=topic, event=event.key.urlsafe())
        response = self.api.post('/pubsub/pub-multicast', params)
        self._test_response(response)
        tasks = self.taskqueue_stub.get_filtered_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, 'pubsub-pub-event-notification')


class NotifyTest(common.BaseTest):

    def setUp(self):
        super(NotifyTest, self).setUp()
        app = webapp2.WSGIApplication(
            [(r'/pubsub/pub-event-notification', api.NotificationHandler)])
        self.api = webtest.TestApp(app)

    def _test_response(self, response):
        self.assertEqual(response.status_int, 201)
        self.assertEqual(response.normal_body, '"{\\"success\\": true}"')
        self.assertEqual(response.content_type, 'application/json')

    def testNotify(self):
        topic = 'alerts/forma'
        geojson = """{
                      "type":"Polygon",
                      "coordinates":[
                        [
                          [
                            -58.97460937499999,
                            -4.12728532324537
                          ],
                          [
                            -60.732421875,
                            -7.798078531355291
                          ],
                          [
                            -55.634765625,
                            -7.972197714386866
                          ],
                          [
                            -54.84375,
                            -4.653079918274038
                          ],
                          [
                            -58.97460937499999,
                            -4.12728532324537
                          ]
                        ]
                      ]
                    }"""
        params = dict(geojson=geojson)
        s = api.Subscription(
            topic=topic, params=params, email='foo', confirmed=True)
        s.put()
        event = api.Event(topic=topic)
        event.created = datetime.strptime('Jan 1 2014', '%b %d %Y')
        event.put()
        event = api.Event(topic=topic)
        event.put()
        params = dict(topic=topic, event=event.key.urlsafe(),
                      subscription=s.key.urlsafe())
        response = self.api.post(
            '/pubsub/pub-event-notification', params)
        self._test_response(response)


if __name__ == '__main__':
    unittest.main(exit=False, failfast=True)
