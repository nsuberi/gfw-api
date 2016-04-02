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

def send_confirmation_email(email, user_name, urlsafe):
    """Sends a confirmation email for a subscription request.

    Args:
      email: Address to mail to.
      urlsafe: Subscription model urlsafe key.
    """
    subscription = ndb.Key(urlsafe=urlsafe).get()
    topic = subscription.topic

    url_base = runtime_config['APP_BASE_URL']
    conf_url = '%s/v2/subscriptions/%s/confirm' % (url_base, subscription.key.id())

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
