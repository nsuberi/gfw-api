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

from gfw.middlewares.cors import CORSRequestHandler
from gfw.mailers.subscription_confirmation import SubscriptionConfirmationMailer
from gfw.models.subscription import Subscription

from google.appengine.ext import ndb

class SubscriptionsTaskApi(CORSRequestHandler):
    def send_confirmation(self):
        token = self.args().get('subscription')
        subscription = ndb.Key(urlsafe=token).get()

        if subscription:
            mailer = SubscriptionConfirmationMailer(subscription)
            mailer.send()
