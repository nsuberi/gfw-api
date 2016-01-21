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
import logging
import webapp2

from google.appengine.ext import ndb

from appengine_config import runtime_config

import urllib
from google.appengine.api import urlfetch

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


def send_mail_notification(email, topic, name, data, summary):
    """Sends a notification email for a publication event.

    Data contains:
    - params' that were part of the cartodb query.
      EX for forma:
       'params': {'version': 'v1', 'begin': '10-10-2008', 'iso': 'IND', 'end': '12-10-2008'}

     - 'value'
        the alert count

    Variables for Mandrill Template:
      email: Address to mail to. - provided as param
      selected_area: - TODO
      alert_count: - in data.value.
      alert_type: - provided as param.
      alert_date: - in data.params.begin and data.params.end
      alert_summary: - metadata - ex: http://api.globalforestwatch.org//forest-change/forma-alerts/admin/ESP?thresh=30&begin=2006-01-01&end=2009-01-01
      alert_name: - the user's name for the subscription - provided as param 'name'
      alert_link: - to view/download the data. In data.download_urls.csv
    """
    logging.info("Send Notification Email: %s" % email)

    params = data.get('params')
    begin = params.get('begin')
    end = params.get('begin')
    csv = data.get('download_urls').get('csv')

    if 'iso' in params.keys():
        area = "Country ISO Code: " + params.get('iso')
    else:
        area = "Custom area."

    template_content = []
    message = {
        'global_merge_vars': [
            {
                'content': area, 'name': 'selected_area'
            },
            {
                'content': data.get('value'), 'name': 'alert_count'
            },
            {
                'content': topic, 'name': 'alert_type'
            },
            {
                'content': begin + " to " + end, 'name': 'alert_date'
            },
            {
                'content': summary, 'name': 'alert_summary'
            },
            {
                'content': name, 'name': 'alert_name'
            },
            {
                'content': csv, 'name': 'alert_link'
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
