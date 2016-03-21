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

import webapp2

from gfw import common
from gfw.v2.migrations.handlers import MigrationsApi

routes = [
  webapp2.Route(
    r'/v2/migrations/<migration_id>/migrate',
    name='migrate',
    handler=MigrationsApi,
    handler_method='migrate',
    methods=['GET']
  )
]

handlers = webapp2.WSGIApplication(routes, debug=common.IS_DEV)
