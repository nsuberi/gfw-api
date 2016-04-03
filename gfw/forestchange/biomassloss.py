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

"""This module supports accessing biomass loss data."""

import json
import ee
import logging
import config

from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql
from gfw.forestchange.common import classify_query


def _get_coords(geojson):
    return geojson.get('coordinates')


def _sum_range(data, begin, end):
    return sum(
        [value for key, value in data.iteritems()
            if (key !='carbon') and (int(key) >= int(begin)) and (int(key) < int(end))])

def _get_thresh_image(thresh, asset_id):
    """Renames image bands using supplied threshold and returns image."""
    image = ee.Image(asset_id)

    before = image.select('.*_' + thresh).bandNames()

    after = before.map(
        lambda x: ee.String(x).replace('_.*', ''))

    image = image.select(before, after)
    return image


def _get_region(geom):
    """Return ee.Geometry from supplied GeoJSON object."""
    poly = _get_coords(geom)
    ptype = geom.get('type')
    if ptype.lower() == 'multipolygon':
        region = ee.Geometry.MultiPolygon(poly)
    else:
        region = ee.Geometry.Polygon(poly)
    return region


def _ee_biomass(geom, thresh, asset_id1, asset_id2):
    
    image1 = _get_thresh_image(thresh, asset_id1)
    image2 = ee.Image(asset_id2)
    region = _get_region(geom)

    # Reducer arguments
    reduce_args = {
        'reducer': ee.Reducer.sum(),
        'geometry': region,
        'bestEffort': True,
        'scale': 90
    }

    # Calculate stats 10000 ha, 10^6 to transform from Mg (10^6g) to Tg(10^12g) and 255 as is the pixel value when true.
    area_stats = image2.multiply(image1) \
        .divide(10000 * 255.0 * 1000000) \
        .multiply(ee.Image.pixelArea()) \
        .reduceRegion(**reduce_args)
    
    carbon_stats = image2.multiply(ee.Image.pixelArea().divide(10000)).reduceRegion(**reduce_args)
    area_results = area_stats.combine(carbon_stats).getInfo()

    return area_results

def _ee(geom, thresh, asset_id1):
    
    image = _get_thresh_image(thresh, asset_id1)
    region = _get_region(geom)

    # Reducer arguments
    reduce_args = {
        'reducer': ee.Reducer.sum(),
        'geometry': region,
        'bestEffort': True,
        'scale': 90
    }

    # Calculate stats
    area_stats = image.divide(10000 * 255.0) \
        .multiply(ee.Image.pixelArea()) \
        .reduceRegion(**reduce_args)

    return area_stats.getInfo()

def _dict_unit_transform(data, num):
    dasy = {}
    for key, value in data.iteritems():
        dasy[key] = value*num

    return dasy

def _indicator_selector(row, indicator,begin,end):
    """Return Tons of biomass loss."""
    dasy={}
    if indicator == 4:
            return row[2]['value']

    for i in range(len(row)):
        if (row[i]['indicator_id'] == indicator and row[i]['year']>= int(begin) and row[i]['year']<= int(end)):
            dasy[str(row[i]['year'])] = row[i]['value']
    
    return dasy

def _dates_selector(data,begin,end):
    """Return Tons of biomass loss."""
    dasy = {}
    for key, value in data.iteritems():
        if (int(key)>= int(begin) and int(key)<= int(end)):
            dasy[key] = value
    
    return dasy


class BiomasLossSql(Sql):

    ISO = """
        SELECT iso,boundary,admin0_name as country,  year, thresh, indicator_id, value
        FROM indicators_values
        WHERE iso = UPPER('{iso}')
              AND thresh = {thresh}
              AND iso_and_sub_nat = UPPER('{iso}')
              AND boundary = 'admin'
              AND (indicator_id = 1 
                OR indicator_id = 4
                OR indicator_id= 12
                OR indicator_id= 13
                OR indicator_id= 14)
        ORDER BY year, indicator_id"""

    ID1 = """
        SELECT iso, boundary, admin0_name, sub_nat_id as id1,  year, thresh, indicator_id, value
        FROM indicators_values
        WHERE iso = UPPER('{iso}')
              AND thresh = {thresh}
              AND sub_nat_id = {id1}
              AND boundary = 'admin' 
              AND (indicator_id = 1 
                OR indicator_id = 4
                OR indicator_id= 12
                OR indicator_id= 13
                OR indicator_id= 14)
              
        ORDER BY year"""

    IFL = """
        SELECT ST_AsGeoJson(the_geom) AS geojson, type
        FROM gadm_countries_ifl
        WHERE iso = UPPER('{iso}')
        AND type='intact'"""

    IFL_ID1 = """
        SELECT ST_AsGeoJson(the_geom) AS geojson, type
        FROM gadm_countries_ifl
        WHERE iso = UPPER('{iso}')
              AND id1 = {id1}
        AND type='intact'"""

    USE = """
        SELECT ST_AsGeoJson(the_geom) AS geojson
        FROM {use_table}
        WHERE cartodb_id = {pid}"""

    WDPA = """
        SELECT CASE when marine::numeric = 2 then null
        when ST_NPoints(the_geom)<=18000 THEN ST_AsGeoJson(the_geom)
       WHEN ST_NPoints(the_geom) BETWEEN 18000 AND 50000 THEN ST_AsGeoJson(ST_RemoveRepeatedPoints(the_geom, 0.001))
      ELSE ST_AsGeoJson(ST_RemoveRepeatedPoints(the_geom, 0.005))
       END as geojson FROM wdpa_protected_areas where wdpaid={wdpaid}"""

    @classmethod
    def download(cls, sql):
        """ TODO """
        return ""

    @classmethod
    def ifl(cls, params, args):
        params['thresh'] = args['thresh']
        return super(BiomasLossSql, cls).ifl(params, args)

    @classmethod
    def ifl_id1(cls, params, args):
        params['thresh'] = args['thresh']
        return super(BiomasLossSql, cls).ifl_id1(params, args)

    @classmethod
    def iso(cls, params, args):
        params['thresh'] = args['thresh']
        return super(BiomasLossSql, cls).iso(params, args)

    @classmethod
    def id1(cls, params, args):
        params['thresh'] = args['thresh']
        return super(BiomasLossSql, cls).id1(params, args)

    @classmethod
    def use(cls, params, args):
        params['thresh'] = args['thresh']
        return super(BiomasLossSql, cls).use(params, args)

    @classmethod
    def wdpa(cls, params, args):
        params['thresh'] = args['thresh']
        return super(BiomasLossSql, cls).wdpa(params, args)


def _executeIso(args):
    """Query national by iso code."""
    action, data = CartoDbExecutor.execute(args, BiomasLossSql)
    if action == 'error':
        return action, data
    begin = args.get('begin').split('-')[0]
    end = args.get('end').split('-')[0]
    rows = data['rows']
    data.pop('rows')
    data.pop('download_urls')
    data['tree_loss_by_year'] = _indicator_selector(rows, 1, begin, end)
    data['biomass_loss_by_year'] = _indicator_selector(rows, 12, begin, end)
    data['c_loss_by_year'] = _indicator_selector(rows, 13, begin, end)
    data['co2_loss_by_year'] = _indicator_selector(rows, 14, begin, end)
    data['biomass'] = _indicator_selector(rows, 4, begin, end)
    data['biomass_loss'] = _sum_range(data['biomass_loss_by_year'], begin, end)
    
    return action, data


def _executeId1(args):
    """Query subnational by iso code and GADM id."""
    action, data = CartoDbExecutor.execute(args, BiomasLossSql)
    if action == 'error':
        return action, data
    begin = args.get('begin').split('-')[0]
    end = args.get('end').split('-')[0]
    rows = data['rows']
    data.pop('rows')
    data.pop('download_urls')
    data['tree_loss_by_year'] = _indicator_selector(rows, 1, begin, end)
    data['biomass_loss_by_year'] = _indicator_selector(rows, 12, begin, end)
    data['c_loss_by_year'] = _indicator_selector(rows, 13, begin, end)
    data['co2_loss_by_year'] = _indicator_selector(rows, 14, begin, end)
    data['biomass'] = _indicator_selector(rows, 4, begin, end)
    data['biomass_loss'] = _sum_range(data['biomass_loss_by_year'], begin, end)
    return action, data


def _executeIfl(args):
    """Query national by iso code."""
    action, data = CartoDbExecutor.execute(args, BiomasLossSql)
    if action == 'error':
        return action, data
    rows = data['rows']
    data.pop('rows')
    data.pop('download_urls')
    data['years'] = rows
    return action, data


def _executeIflId1(args):
    """Query subnational by iso code and GADM id."""
    action, data = CartoDbExecutor.execute(args, BiomasLossSql)
    if action == 'error':
        return action, data
    rows = data['rows']
    data.pop('rows')
    data.pop('download_urls')
    data['years'] = rows
    return action, data


def _execute_geojson(args):
    """Query GEE using supplied args with threshold and geojson."""

    # Authenticate to GEE and maximize the deadline
    ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
    ee.data.setDeadline(60000)

    # The forest cover threshold and polygon
    thresh = str(args.get('thresh'))
    geojson = json.loads(args.get('geojson'))
    # hansen tree cover loss by year
    hansen_loss_by_year = _ee(geojson, thresh, config.assets['hansen_loss_thresh'])
    logging.info('TREE_LOSS_RESULTS: %s' % hansen_loss_by_year)
    # Biomass loss by year
    loss_by_year = _ee_biomass(geojson, thresh, config.assets['hansen_loss_thresh'], config.assets['biomass_2000'])
    logging.info('BIOMASS_LOSS_RESULTS: %s' % loss_by_year)
    # biomass (UMD doesn't permit disaggregation of forest gain by threshold).
    biomass = loss_by_year['carbon']
    logging.info('BIOMASS: %s' % biomass)
    loss_by_year.pop("carbon",None)

    # Carbon (UMD doesn't permit disaggregation of forest gain by threshold).
    carbon_loss = _dict_unit_transform(loss_by_year, 0.5)
    logging.info('CARBON: %s' % carbon_loss)

    # CO2 (UMD doesn't permit disaggregation of forest gain by threshold).
    carbon_dioxide_loss = _dict_unit_transform(carbon_loss, 3.67)
    logging.info('CO2: %s' % carbon_dioxide_loss)

    # Reduce loss by year for supplied begin and end year
    begin = args.get('begin').split('-')[0]
    end = args.get('end').split('-')[0]
    biomass_loss = _sum_range(loss_by_year, begin, end)

    # Prepare result object
    result = {}
    result['params'] = args
    result['params']['geojson'] = json.loads(result['params']['geojson'])
    result['biomass'] = biomass
    result['biomass_loss'] = biomass_loss
    result['biomass_loss_by_year'] = _dates_selector(loss_by_year,begin,end)
    result['tree_loss_by_year'] = _dates_selector(hansen_loss_by_year,begin,end)
    result['c_loss_by_year'] = _dates_selector(carbon_loss,begin,end)
    result['co2_loss_by_year'] = _dates_selector(carbon_dioxide_loss,begin,end)

    return 'respond', result


def _executeWdpa(args):
    """Query GEE using supplied WDPA id."""
    action, data = CartoDbExecutor.execute(args, BiomasLossSql)
    if action == 'error':
        return action, data
    rows = data['rows']
    data.pop('rows')
    data.pop('download_urls')
    if rows[0]['geojson']==None:
        args['geojson'] = rows[0]['geojson']
        args['begin'] = args['begin'] if 'begin' in args else '2001-01-01'
        args['end'] = args['end'] if 'end' in args else '2013-01-01'
        data['params'].pop('geojson')
        data['gain'] = None
        data['loss'] = None
        data['tree-extent'] = None
        data['biomass'] = None
        data['biomass_loss'] = None
        data['biomass_loss_by_year'] = None
        data['c_loss_by_year'] = None
        data['co2_loss_by_year'] = None
    elif rows:
        args['geojson'] = rows[0]['geojson']
        args['begin'] = args['begin'] if 'begin' in args else '2001-01-01'
        args['end'] = args['end'] if 'end' in args else '2013-01-01'
        action, data = _execute_geojson(args)
        data['params'].pop('geojson')
    return action, data


def _executeUse(args):
    """Query GEE using supplied concession id."""
    action, data = CartoDbExecutor.execute(args, BiomasLossSql)
    if action == 'error':
        return action, data
    rows = data['rows']
    data.pop('rows')
    data.pop('download_urls')
    if rows:
        args['geojson'] = rows[0]['geojson']
        args['begin'] = args['begin'] if 'begin' in args else '2001-01-01'
        args['end'] = args['end'] if 'end' in args else '2013-01-01'
        action, data = _execute_geojson(args)
        data['params'].pop('geojson')
    return action, data


def _executeWorld(args):
    """Query GEE using supplied args with threshold and polygon."""
    return _execute_geojson(args)


def execute(args):
    if 'begin' in args:
        args['begin'] = args['begin'].strftime('%Y-%m-%d')
    if 'end' in args:
        args['end'] = args['end'].strftime('%Y-%m-%d')

    query_type = classify_query(args)

    # Set default threshold
    if 'thresh' not in args:
        args['thresh'] = 30

    if query_type == 'iso':
        return _executeIso(args)
    elif query_type == 'id1':
        return _executeId1(args)
    elif query_type == 'ifl':
        return _executeIfl(args)
    elif query_type == 'ifl_id1':
        return _executeIflId1(args)
    elif query_type == 'use':
        return _executeUse(args)
    elif query_type == 'wdpa':
        return _executeWdpa(args)
    elif query_type == 'world':
        return _executeWorld(args)
