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
from google.appengine.api import urlfetch

IMAGE_SERVER = "http://gis-gfw.wri.org/arcgis/rest/services/image_services/glad_alerts_analysis/ImageServer/computeHistograms"

START_YEAR = 2015

MOSAIC_RULE = {
    "mosaicMethod": "esriMosaicLockRaster",
    "ascending": True,
    "mosaicOperation": "MT_FIRST"
}

def generateMosaicRule(raster):
    mosaicRule = MOSAIC_RULE
    mosaicRule['lockRasterIds'] = [raster]
    return mosaicRule

def geojsonToEsriJson(geojson):
    geojson = json.loads(geojson)
    geojson['type'] = 'polygon'
    geojson['rings'] = geojson.pop('coordinates')

    return geojson

def dateToGridCode(date):
    return date.timetuple().tm_yday + (365 * (date.year - START_YEAR))

def rasterForDate(date):
    return (date.year - START_YEAR) + 1

def rastersForPeriod(startDate, endDate):
    rasters = set([])
    rasters.update([rasterForDate(startDate)])
    rasters.update([rasterForDate(endDate)])

    return list(rasters)

def getHistogram(rasters, esri_json):
    form_fields = {
        "geometry": json.dumps(esri_json),
        "geometryType": "esriGeometryPolygon",
        "f": "pjson"
    }

    results = []
    for raster in rasters:
        print form_fields
        form_fields['mosaicRule'] = generateMosaicRule(raster)
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(url=IMAGE_SERVER,
            payload=form_data,
            method=urlfetch.POST,
            deadline=60,
            headers={'Content-Type': 'application/x-www-form-urlencoded'})

        result = json.loads(result.content)
        if 'error' not in result:
            results.append(result)

    return results

def alertCount(begin, end, histograms):
    print histograms
    counts = reduce(lambda t, histogram: t + histogram['histograms'][0]['counts'], histograms, [])
    beginIndex = dateToGridCode(begin) - 1
    endIndex = dateToGridCode(end) - 1
    counts_for_period = counts[beginIndex:endIndex]

    return sum(counts_for_period)

def decorateWithArgs(dictionary, args):
    dictionary['params'] = args
    dictionary['params']['geojson'] = json.loads(dictionary['params']['geojson'])

    return dictionary

def execute(args):
    begin = args.get('begin')
    end = args.get('end')
    rasters = rastersForPeriod(begin, end)
    esri_json = geojsonToEsriJson(args.get('geojson'))
    alert_count = alertCount(begin, end, getHistogram(rasters, esri_json))

    return 'respond', decorateWithArgs({
        "min_date": begin.isoformat(),
        "max_date": end.isoformat(),
        "value": alert_count
    }, args)
