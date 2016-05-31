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
    geojson['spatialReference'] = { 'wkid': 4326 }

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
    # esri_json = {
      # "type": "polygon",
      # "rings": [ [ [12473969, -229999], [12473985, -229101], [12467938, -229083], [12466906, -224960], [12467378, -224828], [12468799, -225243], [12469676, -224640], [12472019, -223848], [12473324, -222685], [12473969, -221497], [12473280, -220781], [12473152, -219744], [12473907, -219493], [12473970, -218400], [12473596, -218258], [12473671, -216842], [12474477, -216363], [12474225, -217285], [12474691, -218229], [12476053, -218949], [12475514, -219645], [12475807, -220220], [12478711, -220244], [12480163, -222465], [12480843, -222391], [12481148, -223069], [12481813, -222758], [12481637, -223111], [12482266, -224104], [12481236, -224112], [12483424, -227510], [12479852, -229496], [12478617, -228545], [12478030, -229179], [12477498, -228847], [12476894, -229905], [12473969, -229999] ] ],
      # "spatialReference": {
        # "wkid": 102100,
        # "latestWkid": 3857
      # }
    # }

    form_fields = {
        "geometry": json.dumps(esri_json),
        "geometryType": "esriGeometryPolygon",
        "pixelSize": 30,
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
