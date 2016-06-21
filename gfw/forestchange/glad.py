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

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql

request_notes = []

class GeometrySql(Sql):
    ISO = """
        SELECT ST_AsGeoJSON(the_geom) AS geojson
        FROM gadm2_countries_simple
        WHERE iso = UPPER('{iso}')"""

    ID1 = """
        SELECT ST_AsGeoJSON(the_geom) AS geojson
        FROM gadm2_provinces_simple
        WHERE iso = UPPER('{iso}')
          AND id_1 = {id1}"""

    WDPA = """
        SELECT ST_AsGeoJSON(p.the_geom) AS geojson
        FROM (
          SELECT CASE
          WHEN marine::numeric = 2 THEN NULL
            WHEN ST_NPoints(the_geom)<=18000 THEN the_geom
            WHEN ST_NPoints(the_geom) BETWEEN 18000 AND 50000 THEN ST_RemoveRepeatedPoints(the_geom, 0.001)
            ELSE ST_RemoveRepeatedPoints(the_geom, 0.005)
            END AS the_geom
          FROM wdpa_protected_areas
          WHERE wdpaid={wdpaid}
        ) p"""

    USE = """
        SELECT ST_AsGeoJSON(the_geom) AS geojson
        FROM {use_table}
        WHERE cartodb_id = {pid}"""

    @classmethod
    def download(cls, sql):
        return sql

IMAGE_SERVER = "http://gis-gfw.wri.org/arcgis/rest/services/image_services/glad_alerts_analysis/ImageServer/computeHistograms"
CONFIRMED_IMAGE_SERVER = "http://gis-gfw.wri.org/arcgis/rest/services/image_services/glad_alerts_con_analysis/ImageServer/computeHistograms"

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
    if geojson['type'] == 'Polygon':
        geojson['rings'] = geojson.pop('coordinates')
    elif geojson['type'] == 'MultiPolygon':
        geojson['rings'] = geojson.pop('coordinates')[0]

    geojson['type'] = 'polygon'
    return geojson

def dateToGridCode(date):
    return date.timetuple().tm_yday + (365 * (date.year - START_YEAR))

def rasterForDate(date):
    return (date.year - START_YEAR) + 1

def yearForRaster(raster):
    return (raster - 1) + START_YEAR

def rastersForPeriod(startDate, endDate):
    rasters = set([])
    rasters.update([rasterForDate(startDate)])
    rasters.update([rasterForDate(endDate)])

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
        result = urlfetch.fetch(url=image_server,
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
    dictionary['params']['geojson'] = json.loads(dictionary['params']['geojson'])

    return dictionary

def execute(args):
    begin = args.get('begin')
    end = args.get('end')
    rasters = rastersForPeriod(begin, end)

    if 'geojson' not in args:
        action, data = CartoDbExecutor.execute(args, GeometrySql)
        args['geojson'] = data['rows'][0]['geojson']

    confirmed_only = False
    if 'glad_confirmed_only' in args:
        confirmed_only = True

    esri_json = geojsonToEsriJson(args.get('geojson'))
    alert_count = alertCount(begin, end, getHistogram(rasters, esri_json, confirmed_only))

    return 'respond', decorateWithArgs({
        "min_date": begin.isoformat(),
        "max_date": end.isoformat(),
        "value": alert_count,
        "notes": request_notes
    }, args)
