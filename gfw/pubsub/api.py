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

"""Module that handles all pubsub."""

import copy
import datetime
import json
import logging
import webapp2

from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from gfw.common import CORSRequestHandler
from gfw.forestchange import forma, terrai, imazon, prodes, quicc, umd, guyra
from appengine_config import runtime_config

from gfw.pubsub.subscription import Subscription

import urllib
from google.appengine.api import urlfetch

#import mandrill
#mandrill_client = mandrill.Mandrill(mandrill_key)

class Event(ndb.Model):
    """Model for publication events."""
    topic = ndb.StringProperty()
    created = ndb.DateTimeProperty(
        auto_now_add=True, default=datetime.datetime.now())
    date = ndb.ComputedProperty(lambda self: self.created.strftime('%m-%d-%Y'))

    @classmethod
    def latest(cls, topic):
        """Return the latest event for supplied topic."""
        q = cls.query().filter(cls.topic == topic)
        event = q.order(cls.created).fetch(1)
        if event:
            return event[0]

    @classmethod
    def latest_date(cls, topic):
        """Return string date for latest event with supplied topic."""
        f = '%m-%d-%Y'
        event = cls.latest(topic)
        if event:
            return event.created.strftime(f)


class ArgError(ValueError):
    """Base class for API argument errors."""
    def __init__(self, msg):
        super(ArgError, self).__init__(msg)


class EmailArgError(ArgError):
    USAGE = """Email address must have valid form."""

    def __init__(self):
        msg = 'Invalid email parameter. Usage: %s' % self.USAGE
        super(EmailArgError, self).__init__(msg)


class EventArgError(ArgError):
    USAGE = """Event must be an Event.key.urlsafe() string."""

    def __init__(self):
        msg = 'Invalid event parameter. Usage: %s' % self.USAGE
        super(EventArgError, self).__init__(msg)


class SubscriptionArgError(ArgError):
    USAGE = """Subscription must be an Subscription.key.urlsafe() string."""

    def __init__(self):
        msg = 'Invalid event parameter. Usage: %s' % self.USAGE
        super(SubscriptionArgError, self).__init__(msg)


class NamespaceArgError(ArgError):
    USAGE = """Test parameter must be 0 or 1."""

    def __init__(self):
        msg = 'Invalid test parameter. Usage: %s' % self.USAGE
        super(NamespaceArgError, self).__init__(msg)


class TopicArgError(ArgError):
    USAGE = """Unknown topic."""

    def __init__(self):
        msg = 'Invalid topic parameter. Usage: %s' % self.USAGE
        super(TopicArgError, self).__init__(msg)


class TokenArgError(ArgError):
    USAGE = """Invalid token."""

    def __init__(self):
        msg = 'Invalid token parameter. Usage: %s' % self.USAGE
        super(TokenArgError, self).__init__(msg)


class ArgProcessor():
    """Class for processing API arguments."""

    @classmethod
    def email(cls, value):
        try:
            if '@' not in value:
                raise
            return dict(email=value)
        except:
            raise EmailArgError()

    @classmethod
    def namespace(cls, value):
        try:
            return dict(namespace=value)
        except:
            raise NamespaceArgError()

    @classmethod
    def event(cls, value):
        try:
            return dict(event=value)
        except:
            raise EventArgError()

    @classmethod
    def subscription(cls, value):
        try:
            return dict(subscription=value)
        except:
            raise SubscriptionArgError()

    @classmethod
    def topic(cls, value):
        try:
            if value not in ['alerts/forma', 'alerts/terra', 'alerts/sad',
                            'alerts/quicc', 'alerts/treeloss', 'alerts/treegain',
                            'alerts/prodes', 'alerts/guyra', 'alerts/landsat']:
                raise
            return dict(topic=value)
        except:
            raise TopicArgError()

    @classmethod
    def token(cls, value):
        try:
            if not value:
                raise
            return dict(token=value)
        except:
            raise TokenArgError()

    @classmethod
    def process(cls, args):
        """Process supplied dictionary of args into new dictionary of args."""
        processed = {}
        if not args:
            return processed
        for name, value in args.iteritems():
            if hasattr(cls, name):
                processed.update(getattr(cls, name)(value))
        return processed

mandrill_key = runtime_config.get('mandrill_api_key')
mandrill_url = "https://mandrillapp.com/api/1.0/messages/send-template.json"


def send_mandrill_email(template_name, template_content, message):
    "Send Mandrill Email"
    payload = {"template_content": template_content,
               "template_name": template_name,
               "message": message,
               "key": mandrill_key,
               "async": "false"}

    result = urlfetch.fetch(mandrill_url,
        payload=json.dumps(payload),
        method=urlfetch.POST,
        headers={'Content-Type': 'application/json'})

    return result


def send_mail_notification(email, action, data):
    """Sends a notification email for a publication event.

    Args:
      email: Address to mail to.
      selected_area:
      alert_count:
      alert_type:
      alert_date:
      alert_summary:
      alert_specs:
    """
    logging.info("Send Notification Email: %s" % email)

    # TODO: Finish these - get info from 'data':
    template_content = []
    message = {
        'global_merge_vars': [
            {
                'content': "area", 'name': 'selected_area'
            },
            {
                'content': "count", 'name': 'alert_count'
            },
            {
                'content': "type", 'name': 'alert_type'
            },
            {
                'content': "date", 'name': 'alert_date'
            },
            {
                'content': "summary", 'name': 'alert_summary'
            },
            {
                'content': "specs", 'name': 'alert_specs'
            }],
        'to': [
            {
                'email': email,
                'name': 'Recipient Name',
                'type': 'to'}],
        'track_clicks': True,
        'merge_language': 'handlebars',
        'track_opens': True
    }

    result = send_mandrill_email("forest-change-notification", template_content, message)

    logging.info("Send Notification Email Result: %s" % result.content)


def get_deltas(topic, params):
    """Params should contain a begin and end date."""
    if topic == 'alerts/forma':
        action, data = forma.execute(params)
    elif topic == 'alerts/terra':
        action, data = terrai.execute(params)
    elif topic == 'alerts/sad':
        action, data = imazon.execute(params)
    elif topic == 'alerts/quicc':
        action, data = quicc.execute(params)
    elif topic == 'alerts/prodes':
        action, data = prodes.execute(params)
    elif topic == 'alerts/treeloss':
        action, data = umd.execute(params)
    elif topic == 'alerts/treegain':
        action, data = umd.execute(params)
    elif topic == 'alerts/guyra':
        action, data = guyra.execute(params)
    # TODO: 'alerts/landsat'
    return action, data


def notify(params):
    """Send notification to subscriber."""
    event = ndb.Key(urlsafe=params.get('event')).get()
    sub = ndb.Key(urlsafe=params.get('subscription')).get()
    params = copy.copy(sub.params)
    params['begin'] = event.latest_date(event.topic)
    params['end'] = event.date
    logging.info("Notify. Begin: %s End: %s" % (params['begin'], params['end']))
    # If we're running unit tests locally or via travis, skip this:
    if runtime_config.get('APP_VERSION') != 'unittest':
        action, data = get_deltas(event.topic, params)
        send_mail_notification(sub.email, action, data)


def multicast(params):
    """Multicast event notifications.

    Args:
      params: Dictionary containing the event (Event.key.urlsafe())

    The taskqueue API is used for scaling since there could potentially be
    thousands of event notifications to send (which would take too long in a
    regular request). Each discrete event notification is added to the
    queue.
    """
    logging.info("Multicast. Event Key: %s " % params.get('event'))
    event = ndb.Key(urlsafe=params.get('event')).get()
    for subscription in Subscription.by_topic(event.topic):
        logging.info("Multicast. Subscription Key: %s " % subscription.key.urlsafe())
        params['subscription'] = subscription.key.urlsafe()
        taskqueue.add(url='/pubsub/pub-event-notification',
                      queue_name='pubsub-pub-event-notification',
                      params=params)


def publish(params):
    """Publishes notification from supplied params by multicasting.

    The taskqueue API is used for scaling since there could potentially be
    thousands of subscribers (which would take too long in a regular request).
    We add a multicasting task to the queue for the supplied event and that's
    it.
    """
    topic, ns = map(params.get, ['topic', 'namespace'])
    logging.info("Publish. topic: %s namespace: %s" % (topic, ns))
    event = Event(namespace=ns, topic=topic)
    event.put()
    logging.info("Publish. event key: %s" % event.key.urlsafe())
    taskqueue.add(url='/pubsub/pub-multicast',
                  queue_name='pubsub-pub-multicast',
                  params=dict(event=event.key.urlsafe()))


def subscribe(params):
    """Create new Subscribe model from supplied params and return it.

    If 'namespace' is in params, the Subscription model is created within the
    supplied namespace.

    Args:
      params: Dictionary (topic and email keys required, namespace optional).
    """
    topic, email, ns = map(params.get, ['topic', 'email', 'namespace'])
    if topic and email:
        s = Subscription(namespace=ns, topic=topic, email=email, params=params)
        s.put()
        return s


def send_confirmation_email(email, urlsafe):
    """Sends a confirmation email for a subscription request.

    Args:
      email: Address to mail to.
      urlsafe: Subscription model urlsafe key.
    """
    url_base = runtime_config['APP_BASE_URL']
    conf_url = '%s/pubsub/sub-confirm?token=%s' % (url_base, urlsafe)
    template_content = []
    message = {
        'global_merge_vars': [
            {
                'content': conf_url, 'name': 'confirmation_url'
            }],
        'to': [
            {
                'email': email,
                'name': 'Recipient Name',
                'type': 'to'}],
        'track_clicks': True,
        'merge_language': 'handlebars',
        'track_opens': True
    }

    # This does not work locally in GAE:
    # result = mandrill_client.messages.send_template(
    #     template_name='subscription-confirmation',
    #     template_content=template_content,
    #     message=message)

    result = send_mandrill_email("subscription-confirmation", template_content, message)

    logging.info("Send Confirmation Email Result: %s" % result.content)


def receive_confirmation_email(urlsafe):
    """Set Subscription.confirmed to True for supplied urlsafe key.

    Args:
      urlsafe: A urlsafe string for a Subscription entity.

    Raises:
      Exception: If Subscription entity doesn't exist.
    """
    s = ndb.Key(urlsafe=urlsafe).get()
    s.confirmed = True
    s.put()


class NotificationHandler(CORSRequestHandler):

    """Handler for /pubsub/pub-event-notification requests."""

    def post(self):
        self.get()

    def get(self):
        try:
            logging.info("Notification Handler: %s" % self.args())
            params = ArgProcessor.process(self.args())
            notify(params)
            self.response.set_status(201)
            self.complete('respond', json.dumps(dict(success=True)))
        except (Exception), e:
            logging.exception(e)
            self.write_error(400, e.message)


class MulticastHandler(CORSRequestHandler):

    """Handler for /pubsub/pub-multicast requests."""

    def post(self):
        self.get()

    def get(self):
        try:
            logging.info("Multicast Handler: %s" % self.args())
            params = ArgProcessor.process(self.args())
            multicast(params)
            self.response.set_status(201)
            self.complete('respond', json.dumps(dict(success=True)))
        except (Exception), e:
            logging.exception(e)
            self.write_error(400, e.message)


class PublishHandler(CORSRequestHandler):

    """Handler for /pubsub/pub requests."""

    def post(self):
        self.get()

    def get(self):
        try:
            logging.info("Publish Handler: %s" % self.args())
            params = ArgProcessor.process(self.args())
            publish(params)
            self.response.set_status(201)
            self.complete('respond', json.dumps(dict(success=True)))
        except (Exception), e:
            logging.exception(e)
            self.write_error(400, e.message)


class SubscribeHandler(CORSRequestHandler):

    """Handler for /subscribe requests."""

    def post(self):
        self.get()

    def get(self):
        # Subscribe to given topic, send confirmation email,
        # respond with {success: true}
        try:
            params = ArgProcessor.process(self.args())
            s = subscribe(params)
            send_confirmation_email(s.email, s.key.urlsafe())
            self.response.set_status(201)
            self.complete('respond', json.dumps(dict(success=True)))
        except (Exception), e:
            logging.exception(e)
            self.write_error(400, e.message)


class SubscribeConfirmHandler(CORSRequestHandler):

    """Handler for /sub-confirm requests."""

    def post(self):
        self.get()

    def get(self):
        try:
            params = ArgProcessor.process(self.args())
            receive_confirmation_email(params.get('token'))
            self.response.set_status(200)
            self.complete('respond', json.dumps(dict(status='confirmed')))
        except (Exception), e:
            logging.exception(e)
            self.write_error(400, e.message)


handlers = webapp2.WSGIApplication([
    (r'/pubsub/sub', SubscribeHandler),
    (r'/pubsub/pub', PublishHandler),
    (r'/pubsub/pub-multicast', MulticastHandler),
    (r'/pubsub/sub-confirm', SubscribeConfirmHandler),
    (r'/pubsub/pub-event-notification', NotificationHandler)],
    debug=True)
