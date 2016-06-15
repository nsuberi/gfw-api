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

from sparkpost import SparkPost
sparkpost = SparkPost(runtime_config.get('sparkpost_api_key') or 'sparkpostapikey')

class ContactFormMailer:
    def __init__(self, email):
        self.email = email

    def send(self):
        if self.email.opt_in == True:
            opt_in = 'Yes'
        else:
            opt_in = 'No'

        response = sparkpost.transmissions.send(
            recipients=[{'address': self.email.email_for_topic()}],
            template='contact-form',
            substitution_data={
                'user_email': self.email.user_email,
                'message': self.email.message,
                'topic': self.email.pretty_topic(),
                'opt_in': opt_in
            }
        )

        logging.info("Send Contact Email Result: %s" % response)
