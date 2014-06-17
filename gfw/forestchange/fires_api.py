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

"""This module is the entry point for the NASA Active Fires API."""

import logging

from gfw.forestchange import fires, args
from gfw.common import CORSRequestHandler, APP_BASE_URL

API_BASE = '%s/forest-change/nasa-active-fires' % APP_BASE_URL

META = {
    'meta': {
        "description": "Displays fire alert data for the past 7 days.",
        "resolution": "1000 x 1000 meters",
        "coverage": "Global",
        "timescale": "Past 7 days",
        "updates": "Daily",
        "source": "MODIS",
        "units": "Fires",
        "name": "NASA Active Fires",
        "id": "nasa-fires"
    },
    'apis': {
        'global': '%s{?period,geojson,download,bust,dev}' % API_BASE,
        'national': '%s/admin{/iso}{?period,download,bust,dev}' %
        API_BASE,
        'subnational': '%s/admin{/iso}{/id1}{?period,download,bust,dev}' %
        API_BASE,
        'use': '%s/use/{/name}{/id}{?period,download,bust,dev}' %
        API_BASE,
        'wdpa': '%s/wdpa/{/id}{?period,download,bust,dev}' %
        API_BASE
    }
}


class FiresAllHandler(CORSRequestHandler):
    """Handler for /forest-change/nasa-active-fires"""

    PARAMS = ['period', 'download', 'geojson', 'dev', 'bust']

    def get(self):
        try:
            raw_args = self.args(only=self.PARAMS)
            query_args = args.process(raw_args)
            rid = self.get_id(query_args)
            action, data = self.get_or_execute(query_args, fires, rid)
            if action != 'redirect':
                data.update(META['meta'])
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FiresIsoHandler(CORSRequestHandler):
    """"Handler for /forest-change/nasa-active-fires/admin/{iso}"""

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
            action, data = self.get_or_execute(query_args, fires, rid)
            if action != 'redirect':
                data.update(META['meta'])
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FiresIsoId1Handler(CORSRequestHandler):
    """"Handler for /forest-change/nasa-active-fires/admin/{iso}/{id1}"""

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
            action, data = self.get_or_execute(query_args, fires, rid)
            if action == 'error':
                raise data
            if action != 'redirect':
                data.update(META['meta'])
            self.complete(action, data)
        except (args.ArgError, Exception) as e:
            logging.exception(e)
            self.write_error(400, e.message)


class FiresWdpaHandler(CORSRequestHandler):
    """"Handler for /forest-change/nasa-active-fireswdpa/{wdpaid}"""

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
            action, data = self.get_or_execute(query_args, fires, rid)
            if action != 'redirect':
                data.update(META['meta'])
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)


class FiresUseHandler(CORSRequestHandler):
    """"Handler for /forest-change/nasa-active-fires/use/{use}/{useid}"""

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
            action, data = self.get_or_execute(query_args, fires, rid)
            if action != 'redirect':
                data.update(META['meta'])
            self.complete(action, data)
        except args.ArgError, e:
            logging.exception(e)
            self.write_error(400, e.message)
