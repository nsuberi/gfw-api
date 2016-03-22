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

import webapp2

from engineauth import models

from google.appengine.ext import ndb
from google.appengine.api import taskqueue

class GFWUser(models.User):
    def get_profile(self):
        profile_key = self.auth_ids[0]

        if profile_key:
            return ndb.Key('UserProfile', profile_key).get()

    def _pre_put_hook(self):
        taskqueue.add(url='/user/tasks/tester',
            queue_name='user-tester-sign-up',
            params={'id': self.auth_ids[0]})
        taskqueue.add(url='/user/tasks/profile',
            queue_name='user-profile',
            params={'id': self.key.id()})
