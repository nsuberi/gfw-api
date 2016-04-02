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

import logging

from appengine_config import runtime_config

from gfw.common import gfw_url
from gfw.models.topic import Topic

from sparkpost import SparkPost
sparkpost = SparkPost(runtime_config.get('sparkpost_api_key'))

class SubscriptionConfirmationMailer:
    def __init__(self, subscription):
        self.subscription = subscription
        self.topic = Topic.get_by_id(subscription.topic)

    def send(self):
        url_base = runtime_config['APP_BASE_URL']
        url = '%s/v2/subscriptions/%s/confirm' % (url_base, self.subscription.key.id())

        email = self.subscription.email
        user_profile = self.subscription.user_id.get().get_profile()
        name = getattr(user_profile, 'name', email)

        response = sparkpost.transmissions.send(
            recipients=[{'address': { 'email': email, 'name': name }}],
            template='subscription-confirmation',
            substitution_data={
                'confirmation_url': url,
                'dataset_name': self.topic.description
            }
        )

        logging.info("Send Confirmation Email Result: %s" % response)
