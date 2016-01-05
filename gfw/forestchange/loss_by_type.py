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
import config

import urllib
from google.appengine.api import urlfetch

from dateutil.parser import parse as parseDate

LABELS = ["Agriculture", "Mixed agriculture and forest",
    "Open broadleaved forest", "Closed broadleaved forest",
    "Open needleleaved forest", "Closed needleleaved forest",
    "Open mixed forest", "Mixed forest and grassland",
    "Grassland / shrub", "Flooded forest", "Wetland", "Settlements",
    "Bare land", "Water bodies", "Snow / ice", "No data"]

def _generate_rendering_rule(period):
    start_year = period[0]
    end_year   = period[1]

    return {
        "rasterFunction": "Arithmetic",
        "rasterFunctionArguments": {
            "Raster": {
                "rasterFunction": "Arithmetic",
                "rasterFunctionArguments": {
                    "Raster": {
                        "rasterFunction": "Remap",
                        "rasterFunctionArguments": {
                            "InputRanges": [1, (end_year-start_year+1)],
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
            "Operation": 1
        }
    }

DEFAULT_START_YEAR = 2000
DEFAULT_END_YEAR = 2014

def _get_period(args):
    """Parse the date parameters and return the year value"""

    start_year = DEFAULT_START_YEAR
    end_year = DEFAULT_END_YEAR
    if args.get('begin') and args.get('end'):
        start_year = parseDate(args.get('begin')).year
        end_year = parseDate(args.get('end')).year

    return (start_year, end_year)

def _get_esri_json(args):
    """Converts GeoJSON in to Esri JSON"""

    geojson = json.loads(args.get('geojson'))
    geojson['rings'] = geojson.pop('coordinates')
    geojson['spatialReference'] = { 'wkid': 4326 }

    return geojson

def _get_histogram(period, esri_json):
    """Retrieve the histogram values from ArcGIS server for the given time and geometry"""

    form_fields = {
        "geometry": esri_json,
        "geometryType": "esriGeometryPolygon",
        "renderingRule": _generate_rendering_rule(period),
        "pixelSize": {"m":"meter", "spatialReference":{"wkid":54012}},
        "f": "pjson"
    }

    form_data = urllib.urlencode(form_fields)
    result = urlfetch.fetch(url="http://gis-gfw.wri.org/arcgis/rest/services/GFW/analysis/ImageServer/computeHistograms",
        payload=form_data,
        method=urlfetch.POST,
        deadline=60,
        headers={'Content-Type': 'application/x-www-form-urlencoded'})

    histograms = json.loads(result.content)['histograms']

    return histograms[0] if len(histograms) > 0 else None

def _aggregate_histogram_by_year(period, histogram):
    """Groups the given histogram value by year and land type"""

    years = {}

    if histogram is not None:
        values = histogram['counts']
        year_range = range(period[0], period[1]+1)
        offset = len(LABELS)

        group_by_type = lambda i: dict(zip(LABELS, values[offset*i:offset*i+offset]))
        years = dict([(year, group_by_type(i)) for i, year in enumerate(year_range)])

    return years

def _aggregate_histogram_by_type(period, histogram):
    """Groups the given histogram value by land type"""

    types = {}

    if histogram is not None:
        values = histogram['counts']
        offset = len(LABELS)
        label_range = enumerate(range(0, len(LABELS)-1))

        group_by_type = lambda i: dict(zip(LABELS, values[offset*i:offset*i+offset]))
        values_by_type = [group_by_type(i) for i, label in label_range]
        types = {key: sum(d.get(key, 0) for d in values_by_type) for key in values_by_type[0]}

    return types

def _decorate_with_args(dictionary, args):
    dictionary['params'] = args
    dictionary['params']['geojson'] = json.loads(dictionary['params']['geojson'])

    return dictionary

def execute(args):
    period    = _get_period(args)
    esri_json = _get_esri_json(args)
    histogram = _get_histogram(period, esri_json)

    if args.get('aggregate_by') == 'year':
        results = _aggregate_histogram_by_year(period, histogram)
    else:
        results = _aggregate_histogram_by_type(period, histogram)

    return 'respond', _decorate_with_args(results, args)
