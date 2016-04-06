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

from sparkpost import SparkPost
sparkpost = SparkPost(runtime_config.get('sparkpost_api_key'))

class NewStoryMailer:
    def __init__(self, story):
        self.story = story

    def send(self):
        story_url = gfw_url('stories/%s' % self.story['id'], {})
        name = self.story['name']
        email = self.story['email']

        response = sparkpost.transmissions.send(
            recipients=[{'address': { 'email': email, 'name': name }}],
            template='new-story',
            substitution_data={
                'name': name,
                'story_url': story_url
            }
        )

        logging.info("Send Story Email Result: %s" % response)

class NewStoryWriMailer:
    def __init__(self, story):
        self.story = story

    def send(self):
        story_url = gfw_url('stories/%s' % self.story['id'], {})

        response = sparkpost.transmissions.send(
            recipients=runtime_config.get('wri_emails_stories'),
            template='new-story-wri',
            substitution_data={
                'story_url': story_url
            }
        )

        logging.info("Send Story WRI Email Result: %s" % response)
