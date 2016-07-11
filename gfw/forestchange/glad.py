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

"""This module supports accessing UMD/GLAD data."""

import datetime
import json
import urllib
import collections
from google.appengine.api import urlfetch

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import classify_query
from gfw.lib.geometry_sql import GeometrySql

request_notes = []

IMAGE_SERVER = "http://gis-gfw.wri.org/arcgis/rest/services/image_services/glad_alerts_analysis/ImageServer/"
CONFIRMED_IMAGE_SERVER = "http://gis-gfw.wri.org/arcgis/rest/services/image_services/glad_alerts_con_analysis/ImageServer/"

START_YEAR = 2015

MOSAIC_RULE = {
    "mosaicMethod": "esriMosaicLockRaster",
    "ascending": True,
    "mosaicOperation": "MT_FIRST"
}

RASTERS = {
    'all': {
        '2015': 6,
        '2016': 4
    },
    'confirmed_only': {
        '2015': 7,
        '2016': 5
    }
}

YEAR_FOR_RASTERS = {
    6: 2015,
    7: 2015,
    4: 2016,
    5: 2016
}

def generateMosaicRule(raster):
    mosaicRule = MOSAIC_RULE
    mosaicRule['lockRasterIds'] = [raster]
    return mosaicRule

def geojsonToEsriJson(geojson):
    geojson = json.loads(geojson)
    if geojson['type'] == 'Polygon':
        geojson['rings'] = geojson.pop('coordinates')
    elif geojson['type'] == 'MultiPolygon':
        geojson['rings'] = geojson.pop('coordinates')[0]

    geojson['type'] = 'polygon'
    return geojson

def dateToGridCode(date):
    return date.timetuple().tm_yday + (365 * (date.year - START_YEAR))

def rasterForDate(date, confirmed=False):
    if confirmed:
        return RASTERS['confirmed_only'][str(date.year)]
    else:
        return RASTERS['all'][str(date.year)]

def yearForRaster(raster):
    return YEAR_FOR_RASTERS[raster]

def rastersForPeriod(startDate, endDate, confirmed=False):
    rasters = set([])
    rasters.update([rasterForDate(startDate, confirmed)])
    rasters.update([rasterForDate(endDate, confirmed)])

    return list(rasters)

def getHistogram(rasters, esri_json, confirmed_only):
    form_fields = {
        "geometry": json.dumps(esri_json),
        "geometryType": "esriGeometryPolygon",
        "f": "pjson"
    }

    image_server = IMAGE_SERVER
    if confirmed_only:
        image_server = CONFIRMED_IMAGE_SERVER

    request_notes.append('Rasters IDs:')
    request_notes.append(rasters)
    results = []
    for raster in rasters:
        form_fields['mosaicRule'] = generateMosaicRule(raster)
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=image_server+'computeHistograms',
            payload=form_data,
            method=urlfetch.POST,
            deadline=60,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

        result = json.loads(result.content)
        if 'error' not in result:
            results.append([raster, result])

    return results

def datesToGridCodes(begin, end, raster):
    rasterYear = yearForRaster(raster)

    indexes = []
    if begin.year == rasterYear:
        indexes.append(begin.timetuple().tm_yday - 1)
    else:
        indexes.append(datetime.date(rasterYear, 1, 1).timetuple().tm_yday - 1)

    if end.year == rasterYear:
        indexes.append(end.timetuple().tm_yday - 1)
    else:
        indexes.append(datetime.date(rasterYear, 12, 31).timetuple().tm_yday - 1)

    return indexes

def alertCount(begin, end, histograms):
    total_count = 0
    for raster, histogram in histograms:
        counts = []
        if len(histogram['histograms']) > 0:
            counts = histogram['histograms'][0]['counts']

        indexes = datesToGridCodes(begin, end, raster)

        request_notes.append('Counts:')
        request_notes.append(counts)
        request_notes.append('Getting Indexes:')
        request_notes.append(indexes)
        total_count += sum(counts[indexes[0]:indexes[1]])

    return total_count

def decorateWithArgs(dictionary, args):
    dictionary['params'] = args

    if 'geojson' in dictionary['params']:
        dictionary['params']['geojson'] = json.loads(dictionary['params']['geojson'])

    return dictionary

def getAlertCount(args):
    begin = args.get('begin')
    end = args.get('end')

    if 'geojson' not in args:
        action, data = CartoDbExecutor.execute(args, GeometrySql)
        args['geojson'] = data['rows'][0]['geojson']

    confirmed_only = False
    if 'glad_confirmed_only' in args:
        confirmed_only = True

    rasters = rastersForPeriod(begin, end, confirmed_only)

    esri_json = geojsonToEsriJson(args.get('geojson'))
    alert_count = alertCount(begin, end, getHistogram(rasters, esri_json, confirmed_only))

    return 'respond', decorateWithArgs({
        "min_date": begin.isoformat(),
        "max_date": end.isoformat(),
        "value": alert_count,
        "notes": request_notes
    }, args)

def getMaxDateFromHistograms(histograms):
    year = (len(histograms) - 1) + START_YEAR
    latest_histogram_key = max(histograms.keys())
    day_number = len(histograms[latest_histogram_key])
    return datetime.datetime(year, 1, 1) + datetime.timedelta(day_number-1)

def getFullHistogram(args):
    begin = datetime.datetime.strptime(str(START_YEAR), '%Y')
    end = datetime.datetime.now()
    rasters = rastersForPeriod(begin, end)

    results = {}
    for raster in rasters:
        result = urlfetch.fetch(
            url=IMAGE_SERVER+str(raster)+'/info/histograms?f=pjson',
            method=urlfetch.GET,
            deadline=60,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

        result = json.loads(result.content)
        if 'error' not in result:
            results[yearForRaster(raster)] = result['histograms'][0]['counts']

    return 'respond', decorateWithArgs({
        'min_date': begin.strftime('%Y-%m-%d'),
        'max_date': getMaxDateFromHistograms(results).strftime('%Y-%m-%d'),
        'counts': results
    }, args)

def execute(args):
    query_type = classify_query(args)

    if query_type == 'latest':
        return getFullHistogram(args)
    else:
        return getAlertCount(args)
