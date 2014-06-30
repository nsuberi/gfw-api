# Global Forest Watch API
# Copyright (C) 2014 World Resource Institute
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

"""This module is the entry point for the forest change API."""

import logging

from gfw.forestchange import forma, args
from gfw.common import CORSRequestHandler, APP_BASE_URL

class FormaAllHandler(CORSRequestHandler):
    """Handler for /forest-change/forma-alerts"""

    PARAMS = ['period', 'download', 'geojson', 'dev', 'bust']

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            query_args = args.process(raw_args)
            rid = self.get_id(query_args)
            action, data = self.get_or_execute(query_args, forma, rid)
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FormaIsoHandler(CORSRequestHandler):
    """"Handler for /forest-change/forma-alerts/admin/{iso}"""

    PARAMS = ['period', 'download', 'dev', 'bust']

    @classmethod
    def iso_from_path(cls, path):
        """Return iso code from supplied request path."""
        return path.split('/')[4]

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            raw_args['iso'] = self.iso_from_path(self.request.path)
            query_args = args.process(raw_args)
            rid = self.get_id(query_args)
            action, data = self.get_or_execute(query_args, forma, rid)
            if action != 'redirect':
                data.update(FORMA_META['meta'])
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FormaIsoId1Handler(CORSRequestHandler):
    """"Handler for /forest-change/forma-alerts/admin/{iso}/{id1}"""

    PARAMS = ['period', 'download', 'dev', 'bust']

    @classmethod
    def iso_id1_from_path(cls, path):
        """Return iso code and id1 from supplied request path."""
        return path.split('/')[4], path.split('/')[5]

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            iso, id1 = self.iso_id1_from_path(self.request.path)
            raw_args['iso'] = iso
            raw_args['id1'] = id1
            query_args = args.process(raw_args)
            rid = self.get_id(query_args)
            action, data = self.get_or_execute(query_args, forma, rid)
            if action != 'redirect':
                data.update(FORMA_META['meta'])
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FormaWdpaHandler(CORSRequestHandler):
    """"Handler for /forest-change/forma-alerts/wdpa/{wdpaid}"""

    PARAMS = ['period', 'download', 'dev', 'bust']

    @classmethod
    def wdpaid_from_path(cls, path):
        """Return wdpaid from supplied request path."""
        return path.split('/')[4]

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            raw_args['wdpaid'] = self.wdpaid_from_path(self.request.path)
            query_args = args.process(raw_args)
            rid = self.get_id(query_args)
            action, data = self.get_or_execute(query_args, forma, rid)
            if action != 'redirect':
                data.update(FORMA_META['meta'])
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FormaUseHandler(CORSRequestHandler):
    """"Handler for /forest-change/forma-alerts/use/{use}/{useid}"""

    PARAMS = ['period', 'download', 'dev', 'bust']

    @classmethod
    def use_useid_from_path(cls, path):
        """Return nameid from supplied request path."""
        return path.split('/')[4], path.split('/')[5]

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            use, useid = self.use_useid_from_path(self.request.path)
            raw_args['use'] = use
            raw_args['useid'] = useid
            query_args = args.process(raw_args)
            rid = self.get_id(query_args)
            action, data = self.get_or_execute(query_args, forma, rid)
            if action != 'redirect':
                data.update(FORMA_META['meta'])
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)
