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

from gfw import common
from gfw.admin.pubsub.tasks import PubSubTaskApi
from gfw.admin.pubsub.management import PubSubManagementApi

handlers = webapp2.WSGIApplication([

    webapp2.Route(r'/manage/pubsub',
        handler=PubSubManagementApi,
        handler_method='post',
        methods=['GET', 'POST']),

    webapp2.Route(r'/manage/pubsub/automatic',
        handler=PubSubManagementApi,
        handler_method='automatic',
        methods=['GET']),

    webapp2.Route(r'/manage/pubsub/tasks/publish_subscriptions',
        handler=PubSubTaskApi,
        handler_method='publish_subscriptions',
        methods=['POST']),

    webapp2.Route(r'/manage/pubsub/tasks/publish_subscription',
        handler=PubSubTaskApi,
        handler_method='publish_subscription',
        methods=['POST'])


], debug=common.IS_DEV)
