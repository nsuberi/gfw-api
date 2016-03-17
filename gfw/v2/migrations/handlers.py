# Global Forest Watch API
# Copyright (C) 2013 World Resource Institute
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
import webapp2

from google.appengine.ext import ndb

from gfw.middlewares.cors import CORSRequestHandler
from gfw.common import gfw_url
from appengine_config import runtime_config

from gfw.v2.migrations.migration import Migration
from gfw.pubsub.subscription import Subscription

class MigrationsApi(CORSRequestHandler):
    def dispatch(self):
        options_request = (self.request.method == "OPTIONS")
        self.user = self.request.user if hasattr(self.request, 'user') else None
        if not options_request and self.user is None:
            self.redirect(gfw_url('my_gfw/subscriptions', {}))
        else:
            webapp2.RequestHandler.dispatch(self)

    def migrate(self, migration_id):
        migration = ndb.Key(urlsafe=migration_id).get()
        if migration and migration.key.kind() == Migration.kind:
            migration.update_subscriptions(self.user)
            self.redirect(gfw_url('my_gfw/subscriptions', {
                'migration_successful': True}))
        else:
            self.write_error(404, 'Not found')
