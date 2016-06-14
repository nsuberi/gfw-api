import os
import json
from google.appengine.api import urlfetch
from string import Template
from datetime import date, timedelta

from google.appengine.ext import ndb
from gfw.models.subscription import Subscription

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

def pad(number):
    return number * 1.01

def extent(geojson):
    x, y = zip(*list(explode(geojson['coordinates'])))
    return "%f,%f,%f,%f" % (pad(min(x)), pad(min(y)), pad(max(x)), pad(max(y)))

class SubscriptionOverviewService():
    @classmethod
    def overview_image(cls, subscription):
        geom = subscription.params['geom']
        if 'geometry' in geom:
            geom = geom['geometry']
        extent_str = extent(geom)
        geojson = json.dumps(geom)

        begin = date.today() - timedelta(days=1)
        config = { 'date': begin.strftime('%Y-%m-%d'), 'geojson': geojson.replace('"', '\\"')}
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
            image = urlfetch.fetch(url="http://wri-01.cartodb.com/api/v1/map/static/bbox/%s/%s/700/450.png" % (layergroupid, extent_str), deadline=60)

            if image.status_code == 200:
                return image.content

        raise ValueError("")
