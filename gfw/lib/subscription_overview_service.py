import os
import json
from google.appengine.api import urlfetch
from string import Template
from datetime import date, timedelta

from gfw.forestchange.common import classify_query
from gfw.forestchange.common import CartoDbExecutor
from gfw.forestchange.common import Sql as CartoDbSql

from google.appengine.ext import ndb
from gfw.models.subscription import Subscription

class Sql(object):
    @classmethod
    def clean(cls, sql):
        return ' '.join(sql.split()).replace('"', '\\"')

    @classmethod
    def process(cls, args):
        classification = classify_query(args)

        query = ''
        if hasattr(cls, classification):
            query = getattr(cls, classification)(args)

        if hasattr(cls, classification.upper()):
            query = getattr(cls, classification.upper()).format(**args)

        return cls.clean(query)

    @classmethod
    def use(cls, args):
        concessions = {
            'mining': 'gfw_mining',
            'oilpalm': 'gfw_oil_palm',
            'fiber': 'gfw_wood_fiber',
            'logging': 'gfw_logging'
        }

        args['use_table'] = concessions.get(args['use']) or args['use']
        args['pid'] = args['useid']

        return cls.USE.format(**args)

class GeometrySql(Sql):
    WORLD = """
      SELECT ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON('{geojson}'),4326),3857)
      AS the_geom_webmercator"""

    ISO = """
        SELECT the_geom_webmercator
        FROM gadm2_countries_simple
        WHERE iso = UPPER('{iso}')"""

    ID1 = """
        SELECT the_geom_webmercator
        FROM gadm2_provinces_simple
        WHERE iso = UPPER('{iso}')
          AND id_1 = {id1}"""

    WDPA = """
        SELECT p.the_geom_webmercator
        FROM (
          SELECT CASE
          WHEN marine::numeric = 2 THEN NULL
            WHEN ST_NPoints(the_geom)<=18000 THEN the_geom_webmercator
            WHEN ST_NPoints(the_geom) BETWEEN 18000 AND 50000 THEN ST_RemoveRepeatedPoints(the_geom_webmercator, 0.001)
            ELSE ST_RemoveRepeatedPoints(the_geom_webmercator, 0.005)
            END AS the_geom_webmercator
          FROM wdpa_protected_areas
          WHERE wdpaid={wdpaid}
        ) p"""

    USE = """
        SELECT the_geom_webmercator
        FROM {use_table}
        WHERE cartodb_id = {pid}"""

class BoundingSql(CartoDbSql):
    WORLD = """
      SELECT ST_AsGeojson(ST_Expand(ST_Extent(ST_SetSRID(ST_GeomFromGeoJSON('{geojson}'),4326)),1))
      AS bbox"""

    ISO = """
        SELECT ST_AsGeojson(ST_Expand(ST_Extent(the_geom),1)) AS bbox
        FROM gadm2_countries_simple
        WHERE iso = UPPER('{iso}')"""

    ID1 = """
        SELECT ST_AsGeojson(ST_Expand(ST_Extent(the_geom),1)) AS bbox
        FROM gadm2_provinces_simple
        WHERE iso = UPPER('{iso}')
          AND id_1 = {id1}"""

    WDPA = """
        SELECT ST_AsGeojson(ST_Expand(ST_Extent(p.the_geom),1)) AS bbox
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
        SELECT ST_AsGeojson(ST_Expand(ST_Extent(the_geom),1)) AS bbox
        FROM {use_table}
        WHERE cartodb_id = {pid}"""

    @classmethod
    def download(cls, sql):
        return sql

def explode(coords):
    """Explode a GeoJSON geometry's coordinates object and yield coordinate tuples.
    As long as the input is conforming, the type of the geometry doesn't matter."""
    for e in coords:
        if isinstance(e, (float, int, long)):
            yield coords
            break
        else:
            for f in explode(e):
                yield f

def extent(geojson):
    x, y = zip(*list(explode(geojson['coordinates'])))
    return "%f,%f,%f,%f" % (min(x), min(y), max(x), max(y))

def bbox(args):
    action, bboxResponse = CartoDbExecutor.execute(args, BoundingSql)
    return extent(json.loads(bboxResponse['rows'][0]['bbox']))

class SubscriptionOverviewService():
    @classmethod
    def overview_image(cls, subscription):
        args = subscription.to_dict()

        if 'geom' in subscription.params:
            geom = subscription.params['geom']
            if 'geometry' in geom:
                geom = geom['geometry']
            args['geojson'] = json.dumps(geom)

        args = dict((k, v) for k, v in args.iteritems() if v)

        begin = date.today() - timedelta(days=1)
        config = { 'date': begin.strftime('%Y-%m-%d'), 'query': GeometrySql.process(args)}
        template_file = open(os.path.join(os.path.dirname(__file__), 'templates', 'viirs.json'))
        map_config = Template(template_file.read()).substitute(config)

        result = urlfetch.fetch(url="https://wri-01.cartodb.com/api/v1/map",
            payload=map_config,
            method=urlfetch.POST,
            deadline=60,
            headers={'Content-Type': 'application/json'})
        result = json.loads(result.content)

        if 'layergroupid' in result:
            layergroupid = result['layergroupid']
            image = urlfetch.fetch(url="http://wri-01.cartodb.com/api/v1/map/static/bbox/%s/%s/700/450.png" % (layergroupid, bbox(args)), deadline=60)

            if image.status_code == 200:
                return image.content

        raise ValueError("")
