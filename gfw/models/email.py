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

from google.appengine.ext import ndb
from google.appengine.api import taskqueue

TOPICS = {
    'report-a-bug-or-error-on-gfw': {
        'name': 'Report a bug or error on GFW',
        'emailTo': 'gfw@wri.org'
    },
    'provide-feedback': {
        'name': 'Provide feedback',
        'emailTo': 'gfw@wri.org'
    },
    'media-request': {
        'name': 'Media request',
        'emailTo': 'gfwmedia@wri.org'
    },
    'data-related-inquiry': {
        'name': 'Data related inquiry',
        'emailTo': 'gfwdata@wri.org'
    },
    'gfw-commodities-inquiry': {
        'name': 'GFW Commodities inquiry',
        'emailTo': 'gfwcommodities@wri.org'
    },
    'gfw-fires-inquiry': {
        'name': 'GFW Fires inquiry',
        'emailTo': 'gfwfires@wri.org'
    },
    'gfw-climate-inquiry': {
        'name': 'GFW Climate inquiry',
        'emailTo': 'gfwclimate@wri.org'
    },
    'gfw-water-inquiry': {
        'name': 'GFW Water inquiry',
        'emailTo': 'GFWwater@wri.org'
    },
    'general-inquiry': {
        'name': 'General inquiry',
        'emailTo': 'gfw@wri.org'
    }
}

class Email(ndb.Model):
    user_email = ndb.StringProperty()
    message = ndb.StringProperty()
    topic = ndb.StringProperty()
    opt_in = ndb.BooleanProperty(default=False)

    def _post_put_hook(self, future):
        taskqueue.add(url='/emails/tasks/send',
            queue_name='contact-form-emails',
            params=dict(email=self.key.urlsafe()))

    def pretty_topic(self):
        return TOPICS[self.topic]['name']

    def email_for_topic(self):
        return { 'email': TOPICS[self.topic]['emailTo'] }
