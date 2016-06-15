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

from gfw.email.handlers import EmailApi
from gfw.email.tasks import EmailTaskApi

routes = [

  webapp2.Route(
    r'/emails',
    handler=EmailApi,
    handler_method='send',
    methods=['POST']
  ),

  webapp2.Route(
    r'/emails<:/?.*>',
    handler=EmailApi,
    methods=['OPTIONS']
  ),

  webapp2.Route(r'/emails/tasks/send',
    handler=EmailTaskApi,
    handler_method='send_contact_form',
    methods=['POST'])

]

handlers = webapp2.WSGIApplication(routes, debug=False)
