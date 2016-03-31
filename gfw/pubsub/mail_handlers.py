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
import datetime

from google.appengine.ext import ndb
from appengine_config import runtime_config
from google.appengine.api import urlfetch

from gfw.common import gfw_url

from sparkpost import SparkPost

sparkpost_key = runtime_config.get('sparkpost_api_key')
sparkpost = SparkPost(sparkpost_key)

def alert_description(topic):
    descriptions = {
        'alerts/terra': 'monthly Terra-i tree cover loss alerts',
        'alerts/sad': 'monthly SAD tree cover loss alerts',
        'alerts/quicc': 'quarterly QUICC tree cover loss alerts',
        'alerts/treeloss': 'annual tree cover loss data',
        'alerts/treegain': '12-year tree cover gain data',
        'alerts/prodes': 'annual PRODES deforestation data',
        'alerts/guyra': 'monthly Gran Chaco deforestation data',
        'alerts/glad': 'weekly GLAD tree cover loss alerts',
        'alerts/viirs': 'daily VIIRS active fires alerts',
    }

    return descriptions[topic]

def alert_type_for_topic(topic):
    if topic == 'alerts/forma':
        return "FORMA"
    elif topic == 'alerts/terra':
        return "Terra-i"
    elif topic == 'alerts/sad':
        return "SAD"
    elif topic == 'alerts/quicc':
        return "QUICC tree cover loss alerts (quarterly)"
    elif topic == 'alerts/prodes':
        return "PRODES"
    elif topic == 'alerts/treeloss':
        return "Tree cover loss"
    elif topic == 'alerts/treegain':
        return "Tree cover gain"
    elif topic == 'alerts/guyra':
        return "Gran Chaco deforestation"
    elif topic == 'alerts/glad':
        return "GLAD tree cover loss alerts (weekly)"
    elif topic == 'alerts/viirs':
        return "VIIRS Active fires"
    else:
        return "Unspecified"

def is_count_zero(topic, data):
    """Returns true/false if there has been no change in the analysis
    value since the last alert"""

    simple_results = ['alerts/forma', 'alerts/terra', 'alerts/quicc',
            'alerts/prodes', 'alerts/glad', 'alerts/guyra',
            'alerts/viirs']

    if topic in simple_results:
        count = data.get('value')
        return count == 0 or count == None
    elif topic == 'alerts/sad':
        degradation = data.get('rows')[0].get('value')
        deforestation = data.get('rows')[1].get('value')
        return (degradation == 0) and (deforestation == 0)
    elif (topic == 'alerts/treeloss') | (topic == 'alerts/treegain'):
        gain = data.get('gain')
        loss = data.get('loss')
        return (gain == 0) and (loss == 0)

    return True

def display_counts(topic, data):
    """ Returns a string suitable for display in the 'Alert Counts'
    portion of the Mandrill Email template. """

    if topic in ['alerts/forma', 'alerts/terra', 'alerts/quicc',
            'alerts/glad']:
        count = str(data.get('value')) + " alerts"
    elif topic == 'alerts/prodes' or topic == 'alerts/guyra':
        count = str(data.get('value')) + " ha"
    elif topic == 'alerts/viirs':
        count = str(data.get('value')) + " NASA Active Fires Alerts"
    elif topic == 'alerts/sad':
        a = data.get('rows')[0]
        b = data.get('rows')[1]
        if a.get('data_type') == 'degrad':
            count = "Degradation: " + str(a.get('value')) + \
                    " ha, Deforestation: " + str(b.get('value')) + " ha"
        else:
            count = "Degradation: " + str(b.get('value')) + \
                    " ha, Deforestation: " + str(a.get('value')) + " ha"
    elif (topic == 'alerts/treeloss') | (topic == 'alerts/treegain'):
        count = "Gain: " + str(data.get('gain')) + \
                " ha, Loss: " + str(data.get('loss')) + " ha"

    return count

def send_mail_notification(subscription, email, user_profile, topic, data, summary):
    """Sends a notification email for a publication event.

    Data contains:
    - params' that were part of the cartodb query.
      EX for forma:
       'params': {'version': 'v1', 'begin': '10-10-2008', 'iso': 'IND', 'end': '12-10-2008'}

     - 'value'
        the alert count

    Variables for Mandrill Template:
      email: Address to mail to. - provided as param
      selected_area: - right now works for ISO codes in data.params.
      alert_count: - in data.value.
      alert_type: - provided as param.
      alert_date: - in data.params.begin and data.params.end
      alert_summary: - metadata - ex: http://api.globalforestwatch.org//forest-change/forma-alerts/admin/ESP?thresh=30&begin=2006-01-01&end=2009-01-01
      alert_name: - the user's name for the subscription - provided as param 'name'
      alert_link: - to view/download the data.
    """
    logging.info("Send Notification Email: %s" % email)
    if (is_count_zero(topic, data)):
        logging.info("Cancelled Send Notification Email: No change in analysis")
        return

    params = data.get('params')

    if topic == 'alerts/viirs':
        begin = datetime.datetime.strptime(
            params.get('begin'), "%Y-%m-%d").strftime('%d %b %Y')
        end = datetime.datetime.strptime(
            params.get('end'), "%Y-%m-%d").strftime('%d %b %Y')
    else:
        begin = datetime.datetime.strptime(
            params.get('begin'), "%m-%d-%Y").strftime('%d %b %Y')
        end = datetime.datetime.strptime(
            params.get('end'), "%m-%d-%Y").strftime('%d %b %Y')

    alert_name = params.get('name') or "Unnamed Subscription"
    alert_link = subscription.url
    alert_type = alert_type_for_topic(topic)

    if 'id1' in params.keys():
        area = "ID1: " + params.get('id1')
    elif 'iso' in params.keys():
        area = "ISO Code: " + params.get('iso')
    elif 'wdpaid' in params.keys():
        area = "WDPA ID: " + str(params.get('wdpaid'))
    else:
        area = "Custom area"

    subscriptions_url = gfw_url('my_gfw/subscriptions', {})
    unsubscribe_url = '%s/v2/subscriptions/%s/unsubscribe' % \
        (runtime_config['APP_BASE_URL'], str(subscription.key.id()))

    response = sparkpost.transmissions.send(
        recipients=[
            {
                'address': {
                    'email': email,
                    'name': user_profile.name or email
                }
            }
        ],
        template='forest-change-notification',
        substitution_data={
            'selected_area': area,
            'alert_count': display_counts(topic, data),
            'alert_type': alert_type,
            'alert_date': begin + " to " + end,
            'alert_summary': summary,
            'alert_name': alert_name,
            'alert_link': alert_link,
            'unsubscribe_url': unsubscribe_url,
            'subscriptions_url': subscriptions_url
        }
    )

    logging.info("Send Notification Email Result: %s" % response)

def send_confirmation_email(email, user_name, urlsafe):
    """Sends a confirmation email for a subscription request.

    Args:
      email: Address to mail to.
      urlsafe: Subscription model urlsafe key.
    """
    subscription = ndb.Key(urlsafe=urlsafe).get()
    topic = subscription.topic

    url_base = runtime_config['APP_BASE_URL']
    conf_url = '%s/pubsub/sub-confirm?token=%s' % (url_base, urlsafe)

    response = sparkpost.transmissions.send(
        recipients=[
            {
                'address': {
                    'email': email,
                    'name': user_name or email
                }
            }
        ],
        template='subscription-confirmation',
        substitution_data={
            'confirmation_url': conf_url,
            'dataset_name': alert_description(topic)
        }
    )

    logging.info("Send Confirmation Email Result: %s" % response)


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
