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

"""This module supports accessing forest loff by type data."""

import json
import logging
import config

import urllib
from google.appengine.api import urlfetch

START_YEAR = 2000
END_YEAR = 2014
LABELS = ["Agriculture", "Mixed agriculture and forest",
    "Open broadleaved forest", "Closed broadleaved forest",
    "Open needleleaved forest", "Closed needleleaved forest",
    "Open mixed forest", "Mixed forest and grassland",
    "Grassland / shrub", "Flooded forest", "Wetland", "Settlements",
    "Bare land", "Water bodies", "Snow / ice", "No data"]

def rendering_rule():
    return {
        "rasterFunction": "Arithmetic",
        "rasterFunctionArguments": {
            "Raster": {
                "rasterFunction": "Arithmetic",
                "rasterFunctionArguments": {
                    "Raster": {
                        "rasterFunction": "Remap",
                        "rasterFunctionArguments": {
                            "InputRanges": [1, (END_YEAR-START_YEAR+1)],
                            "OutputValues": [len(LABELS)],
                            "Raster": "$530",
                            "AllowUnmatched": False
                        }
                    },
                    "Raster2": "$530",
                    "Operation": 3
                }
            },
            "Raster2": "$525",
            "Operation":1
        }
    }

def _execute_geojson(geojson):
    """Query GEE using supplied args with threshold and geojson."""

    form_fields = {
        "geometry": geojson,
        "geometryType": "esriGeometryPolygon",
        "renderingRule": rendering_rule(),
        "pixelSize": 100,
        "f": "pjson"
    }

    form_data = urllib.urlencode(form_fields)
    result = urlfetch.fetch(url="http://gis-gfw.wri.org/arcgis/rest/services/GFW/analysis/ImageServer/computeHistograms",
        payload=form_data,
        method=urlfetch.POST,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})

    values = json.loads(result.content)['histograms'][0]['counts']

    year_range = range(START_YEAR, END_YEAR)
    offset = len(LABELS)

    group_by_type = lambda i: dict(zip(LABELS, values[offset*i:offset*i+offset]))
    years = dict([(year, group_by_type(i)) for i, year in enumerate(year_range)])

    return 'respond', years

def execute(args):
    return _execute_geojson(args.get('geojson'))
