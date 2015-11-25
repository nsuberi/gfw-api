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


def _ee(geom, thresh, asset_id1, asset_id2):
    
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

    # Calculate stats
    area_stats = image2.multiply(image1) \
        .divide(10000 * 255.0) \
        .multiply(ee.Image.pixelArea()) \
        .reduceRegion(**reduce_args)
    
    carbon_stats = image2.multiply(ee.Image.pixelArea().divide(10000)).reduceRegion(**reduce_args)
    area_results = area_stats.combine(carbon_stats).getInfo()

    return area_results


def _loss_area(row):
    """Return hectares of loss."""
    return row['year'], row['loss']


def _gain_area(row):
    """Return hectares of gain."""
    return row['year'], row['gain']


class BiomasLossSql(Sql):

    ISO = """
        SELECT iso, country, year, thresh, extent_2000 as extent, extent_perc,
               loss, loss_perc, gain, gain*12 as total_gain, gain_perc
        FROM umd_nat_final_1
        WHERE iso = UPPER('{iso}')
              AND thresh = {thresh}
        ORDER BY year"""

    ID1 = """
        SELECT iso, country, region, year, thresh, extent_2000 as extent,
               extent_perc, loss, loss_perc, gain, gain*12 as total_gain,
               gain_perc, id1
        FROM umd_subnat_final_1
        WHERE iso = UPPER('{iso}')
              AND thresh = {thresh}
              AND id1 = {id1}
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
        SELECT ST_AsGeoJson(the_geom) AS geojson
        FROM wdpa_protected_areas
        WHERE wdpaid={wdpaid}"""

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
    rows = data['rows']
    data.pop('rows')
    data.pop('download_urls')
    data['years'] = rows
    return action, data


def _executeId1(args):
    """Query subnational by iso code and GADM id."""
    action, data = CartoDbExecutor.execute(args, BiomasLossSql)
    if action == 'error':
        return action, data
    rows = data['rows']
    data.pop('rows')
    data.pop('download_urls')
    data['years'] = rows
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

    # Biomass loss by year
    loss_by_year = _ee(geojson, thresh, config.assets['hansen_loss_thresh'], config.assets['biomass_2000'])
    logging.info('BIOMASS_LOSS_RESULTS: %s' % loss_by_year)

    # biomass (UMD doesn't permit disaggregation of forest gain by threshold).
    biomass = loss_by_year['carbon']
    logging.info('BIOMASS: %s' % biomass)

    

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

    return 'respond', result


def _executeWdpa(args):
    """Query GEE using supplied WDPA id."""
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
    query_type = classify_query(args)

    # Set default threshold
    if 'thresh' not in args:
        args['thresh'] = 10

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
