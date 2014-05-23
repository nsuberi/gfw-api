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

"""This module provides functions for dealing with FORMA data."""

import json
import logging

from gfw import cdb
from gfw import common
from gfw import sql


API = "%s/forest-change/forma-alerts{/iso}{/id1}{?period,geojson,use,download}" \
    % common.APP_BASE_URL


META = {
    "description": "Alerts where forest disturbances have likely occurred.",
    "resolution": "500 x 500 meters",
    "coverage": "Humid tropical forest biome",
    "timescale": "January 2006 to present",
    "updates": "16 day",
    "source": "MODIS",
    "units": "Alerts",
    "name": "FORMA",
    "api_url": API,
    "id": "forma-alerts"
}


def _query_response(response, params, query):
    """Return world response."""
    if response.status_code == 200:
        result = json.loads(response.content)['rows'][0]
        result.update(META)
        result.update(params)
        if 'geojson' in params:
            result['geojson'] = json.loads(params['geojson'])
        if 'dev' in params:
            result['dev'] = {'sql': query}
        return result
    else:
        logging.info(query)
        raise Exception(response.content)


def execute(args):
    try:
        query = sql.FormaSql.process(args)
        if 'format' in args:
            return 'redirect', cdb.get_url(query, args)
        else:
            action, response = 'respond', cdb.execute(query)
            return action, _query_response(response, args, query)
    except sql.SqlError, e:
        return 'error', e
