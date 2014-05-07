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

from gfw import cdb
from gfw import sql


META = {
    "description": "Alerts where forest disturbances have likely occurred.",
    "resolution": "500 x 500 meters",
    "coverage": "Humid tropical forest biome",
    "timescale": "Janurary 2006 to present",
    "updates": "16 day",
    "source": "MODIS",
    "units": "Alerts"
}


def query_world(**params):
    args = {}
    args['location'] = """ST_INTERSECTS(ST_SetSRID(
        ST_GeomFromGeoJSON('%s'),4326),the_geom)""" % params['geojson']
    args['begin'] = params['begin']
    args['end'] = params['end']
    query = sql.FORMA_ANALYSIS.format(**args)
    response = cdb.execute(query)
    if response.status_code == 200:
        result = json.loads(response.content)['rows'][0]
        result.update(META)
        result.update(params)
        result['geojson'] = json.loads(result['geojson'])
        return result
    else:
        raise Exception(response.content)
