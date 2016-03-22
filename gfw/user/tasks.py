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

"""This module contains request handlers for user authentication."""

import webapp2

from gfw.middlewares.cors import CORSRequestHandler

from gfw.user.spreadsheets.tester import TesterSpreadsheet
from gfw.user.spreadsheets.profile import ProfileSpreadsheet

from engineauth import models
from engineauth.models import UserProfile

from google.appengine.ext import ndb

class UserTaskApi(CORSRequestHandler):
    def tester(self):
        profile = UserProfile.get_by_id(self.args().get('id'))

        spreadsheet = TesterSpreadsheet()
        spreadsheet.create_or_update(profile)

    def profile(self):
        profile = UserProfile.get_by_id(self.args().get('id'))

        spreadsheet = ProfileSpreadsheet()
        spreadsheet.create_or_update(profile)
