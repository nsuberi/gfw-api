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

"""This NDB entity stores that dates when subscription alerts are sent"""

import copy
import datetime

from google.appengine.ext import ndb

class Event(ndb.Model):
    """Model for publication events."""
    topic = ndb.StringProperty()

    begin = ndb.DateTimeProperty(
        auto_now_add=True, default=datetime.datetime.now())
    end = ndb.DateTimeProperty(
        auto_now_add=True, default=datetime.datetime.now())

    @classmethod
    def latest_for_topic(cls, topic):
        q = cls.query().filter(cls.topic == topic)
        event = q.order(-cls.begin).fetch(1)
        if event:
            return event[0]
