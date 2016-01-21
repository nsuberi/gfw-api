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

"""This module supports stories."""

import json
from appengine_config import runtime_config
from gfw import cdb
import datetime
import os
from string import Template

# API
import webapp2
import re
import hashlib
import base64
import monitor
import random
import traceback
import copy

from google.appengine.api import mail
from google.appengine.api import taskqueue

TABLE = 'stories_dev_copy' if runtime_config.get('IS_DEV') else 'community_stories'


INSERT = """INSERT INTO {table}
  (details, email, name, title, token, visible, date, location,
   the_geom, media)
  VALUES
  ('{details}', '{email}', '{name}', '{title}',
   '{token}', {visible}::boolean, '{date}'::date, '{location}',
   ST_SetSRID(ST_GeomFromGeoJSON('{geom}'), 4326), '{media}')
  RETURNING details, email, name, title, visible, date,
    location, cartodb_id as id, media, ST_AsGeoJSON(the_geom) as the_geom"""


LIST = """SELECT details, email, created_at, name, title, visible, date,
    location, cartodb_id as id, ST_Y(the_geom) AS lat, ST_X(the_geom) AS lng,
    media
FROM {table}
WHERE visible = True {and_where} ORDER BY date ASC"""


GET = """SELECT details, email, name, title, visible, date,
    location, cartodb_id as id, ST_Y(the_geom) AS lat, ST_X(the_geom) AS lng,
    media, ST_AsGeoJSON(the_geom) as the_geom
FROM {table}
WHERE cartodb_id = {id}"""

COUTRY_STORY="""
with iso as (
  SELECT the_geom_webmercator 
  FROM gadm2_provinces_simple 
  WHERE iso = UPPER('{iso}'))
 
    SELECT   cartodb_id as id, date 
    FROM {table} t, iso 
    WHERE visible = True 
    and ST_Intersects(t.the_geom_webmercator, iso.the_geom_webmercator) 
    order by date desc 
    limit 1

"""

COUNT_ISO = """
SELECT COUNT(t.*) AS value
FROM {table} t, 
    (SELECT * FROM gadm2_countries_simple
             WHERE iso = UPPER('{iso}')) as iso
WHERE visible = True 
AND t.created_at >= '{begin}'::date
AND t.created_at <= '{end}'::date 
AND ST_Intersects(t.the_geom, iso.the_geom)
"""

COUNT_GEOM = """
SELECT COUNT(t.*) AS value
FROM {table} t
WHERE visible = True 
AND t.created_at >= '{begin}'::date
AND t.created_at <= '{end}'::date 
AND ST_INTERSECTS(
    ST_SetSRID(
        ST_GeomFromGeoJSON('{geojson}'), 
    4326), 
t.the_geom)"""

def _prep_story(story):
    if 'geom' in story:
        story['geom'] = json.loads(story['geom'])
    if 'media' in story:
        story['media'] = json.loads(story['media'])
    return story


def create_story(params):
    """Create new story with params."""
    props = dict(details='', email='', name='',
                 title='', token='', visible='True', date='',
                 location='', geom='', media='[]', table=TABLE)
    props.update(params)
    for key in ['details', 'title', 'name', 'email', 'location']:
        props[key] = props[key].encode('utf-8').replace("'", "''")
    if not props.get('date'):
        props['date'] = str(datetime.datetime.now())
    props['geom'] = json.dumps(props['geom'])
    if 'media' in props:
        props['media'] = json.dumps(props['media'])
    sql = INSERT.format(**props)
    return cdb.execute(sql, auth=True)

def count_stories(params):
    if params.get('iso'):
        sql = COUNT_ISO
    else:
        sql = COUNT_GEOM

    params['table'] = TABLE
    result = cdb.execute(sql.format(**params), auth=True)
    data = json.loads(result.content)
    rows = data.get('rows')
    if rows:
        return rows[0].get('value') or 0
    else:
        return 0

def list_stories(params):
    and_where = ''
    if 'geom' in params:
        and_where = """AND ST_Intersects(the_geom::geography,
            ST_SetSRID(ST_GeomFromGeoJSON('{geom}'),4326)::geography)"""
    if 'since' in params:
        and_where += """ AND date >= '{since}'::date"""
    if and_where:
        and_where = and_where.format(**params)
    result = cdb.execute(
        LIST.format(and_where=and_where, table=TABLE), auth=True)
    if result:
        data = json.loads(result.content)
        if 'total_rows' in data and data['total_rows'] > 0:
            return map(_prep_story, data['rows'])


def get_story(params):
    params['table'] = TABLE
    result = cdb.execute(GET.format(**params), auth=True)
    if result.status_code != 200:
        raise Exception('CartoDB error getting story (%s)' % result.content)
    if result:
        data = json.loads(result.content)
        if 'total_rows' in data and data['total_rows'] == 1:
            story = data['rows'][0]
            return _prep_story(story)

def get_country_story(params):
    params['table'] = TABLE
    result = cdb.execute(COUTRY_STORY.format(**params), auth=True)
    story_id = json.loads(result.content)
    if story_id['total_rows'] == 1:
        params['id'] = story_id['rows'][0]['id']
        return get_story(params)
    else: 
        return





""" StoriesApi """

class BaseApi(webapp2.RequestHandler):
    """Base request handler for API."""

    def _send_response(self, data, error=None):
        """Sends supplied result dictionnary as JSON response."""
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.response.headers.add_header(
            'Access-Control-Allow-Headers',
            'Origin, X-Requested-With, Content-Type, Accept')
        self.response.headers.add_header('charset', 'utf-8')
        self.response.headers["Content-Type"] = "application/json"
        if error:
            self.response.set_status(400)
        if not data:
            self.response.out.write('')
        else:
            self.response.out.write(data)
        if error:
            taskqueue.add(url='/log/error', params=error, queue_name="log")

    def _get_id(self, params):
        whitespace = re.compile(r'\s+')
        params = re.sub(whitespace, '', json.dumps(params, sort_keys=True))
        return '/'.join([self.request.path.lower(), hashlib.md5(params).hexdigest()])

    def _get_params(self, body=False):
        if body:
            params = json.loads(self.request.body)
        else:
            args = self.request.arguments()
            vals = map(self.request.get, args)
            params = dict(zip(args, vals))
        return params

    def options(self):
        """Options to support CORS requests."""
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Access-Control-Allow-Headers'] = \
            'Origin, X-Requested-With, Content-Type, Accept'
        self.response.headers['Access-Control-Allow-Methods'] = 'POST, GET'


class StoriesApi(BaseApi):

    def _send_new_story_emails(self):
        story = self._get_params()

        # Email WRI:
        subject = 'A new story has been registered with Global Forest Watch'
        sender = \
            'Global Forest Watch Stories <noreply@gfw-apis.appspotmail.com>'
        to = runtime_config.get('wri_emails_stories')
        story_url = '%s/stories/%s' % (runtime_config.get('GFW_BASE_URL'), story['id'])
        api_url = '%s/stories/%s' % (runtime_config.get('APP_BASE_URL'), story['id'])
        token = story['token']
        body = 'Story URL: %s\nStory API: %s\nStory token: %s' % \
            (story_url, api_url, token)
        mail.send_mail(sender=sender, to=to, subject=subject, body=body)

        # Email user:
        config = { 'name': story['name'], 'story_url': story_url }
        txt_path = os.path.join(os.path.dirname(__file__), 'templates', 'story_response.txt')
        txt_file = open(txt_path)
        text_body = Template(txt_file.read()).substitute(config)

        html_path = os.path.join(os.path.dirname(__file__), 'templates', 'story_response.html')
        html_file = open(html_path)
        html_body = Template(html_file.read()).substitute(config)

        subject = 'Your story has been registered with Global Forest Watch!'
        message = mail.EmailMessage(sender=sender, subject=subject)
        message.to = '%s <%s>' % (story['name'], story['email'])
        message.body = text_body
        message.html = html_body
        message.send()

    def _gen_token(self):
        return base64.b64encode(
            hashlib.sha256(str(random.getrandbits(256))).digest(),
            random.choice(
                ['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')

    def list(self):
        try:
            params = self._get_params()
            result = list_stories(params)
            if not result:
                result = []
            self._send_response(json.dumps(result))
        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: Story API (%s)' % name
            monitor.log(self.request.url, msg, error=e,
                        headers=self.request.headers)

    def create(self):
        # host = os.environ['HTTP_HOST']
        # logging.info(os.environ)
        # if 'globalforestwatch' not in host and 'localhost' not in host:
        #     self.error(404)
        #     return
        params = self._get_params(body=True)
        required = ['title', 'email', 'geom']
        if not all(x in params and params.get(x) for x in required):
            self.response.set_status(400)
            self._send_response(json.dumps(dict(required=required)))
            return
        token = self._gen_token()
        try:
            params['token'] = token
            result = create_story(params)
            if result:
                story = json.loads(result.content)['rows'][0]
                story['media'] = json.loads(story['media'])
                data = copy.copy(story)
                data['token'] = token
                self.response.set_status(201)
                taskqueue.add(url='/stories/email', params=data,
                              queue_name="story-new-emails")
                self._send_response(json.dumps(story))
            else:
                story = None
                self.response.set_status(400)
                return
        except Exception, e:
                error = e
                name = error.__class__.__name__
                trace = traceback.format_exc()
                payload = self.request.headers
                payload.update(params)
                msg = 'Story submit failure: %s: %s' % (name, error)
                monitor.log(self.request.url, msg, error=trace,
                            headers=payload)
                self.error(400)

    def get(self, id):
        try:
            params = dict(id=id)
            result = get_story(params)
            if not result:
                self.response.set_status(404)
            self._send_response(json.dumps(result))
        except Exception, e:
            name = e.__class__.__name__
            msg = 'Error: Story API (%s)' % name
            monitor.log(self.request.url, msg, error=e,
                        headers=self.request.headers)

# Stories API routes
CREATE_STORY = r'/stories/new'
LIST_STORIES = r'/stories'
GET_STORY = r'/stories/<id:\d+>'
CREATE_STORY_EMAILS = r'/stories/email'

# Routes
routes = [

    webapp2.Route(CREATE_STORY, handler=StoriesApi,
                  handler_method='create', methods=['POST']),
    webapp2.Route(LIST_STORIES, handler=StoriesApi,
                  handler_method='list'),
    webapp2.Route(GET_STORY, handler=StoriesApi,
                  handler_method='get'),
    webapp2.Route(CREATE_STORY_EMAILS, handler=StoriesApi,
                  handler_method='_send_new_story_emails',
                  methods=['POST'])

]

handlers = webapp2.WSGIApplication(routes, debug=runtime_config.get('IS_DEV'))

