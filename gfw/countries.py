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

"""This module supports accessing countries data."""

import json
from gfw import cdb

ALERTS_ALL_COUNT = """SELECT sum(alerts.count) AS alerts_count
  FROM gfw2_countries AS countries
  LEFT OUTER JOIN (
    SELECT COUNT(*) AS count, iso
      FROM forma_api
      WHERE date >= now() - INTERVAL '12 Months'
      GROUP BY iso)
  AS alerts ON alerts.iso = countries.iso"""


HAS_ALERTS = """SELECT COUNT(*)
  FROM forma_api
  WHERE date >= now() - INTERVAL '12 Months'
  AND iso = upper('{iso}')"""


GET_NO_ALERTS = GET = """SELECT countries.iso, countries.name, countries.enabled,
  countries.lat, countries.lng, countries.extent, countries.gva,
  countries.gva_percent, countries.employment, countries.indepth,
  countries.national_policy_link, countries.national_policy_title,
  countries.convention_cbd, countries.convention_unfccc,
  countries.convention_kyoto, countries.convention_unccd,
  countries.convention_itta, countries.convention_cites,
  countries.convention_ramsar, countries.convention_world_heritage,
  countries.convention_nlbi, countries.convention_ilo, countries.ministry_link,
  countries.external_links, countries.dataset_link, countries.emissions,
  countries.carbon_stocks
  FROM gfw2_countries AS countries
  WHERE iso = upper('{iso}')
  ORDER BY countries.name {order}"""


GET = """SELECT countries.iso, countries.name, countries.enabled, countries.lat,
  countries.lng, countries.extent, countries.gva, countries.gva_percent,
  countries.employment, countries.indepth, countries.national_policy_link,
  countries.national_policy_title, countries.convention_cbd,
  countries.convention_unfccc, countries.convention_kyoto,
  countries.convention_unccd, countries.convention_itta,
  countries.convention_cites, countries.convention_ramsar,
  countries.convention_world_heritage, countries.convention_nlbi,
  countries.convention_ilo, countries.ministry_link, countries.external_links,
  countries.dataset_link, countries.emissions, countries.carbon_stocks,
  alerts.count AS alerts_count
  FROM gfw2_countries AS countries
  {join} OUTER JOIN (
      SELECT COUNT(*) AS count, iso
      FROM forma_api
      WHERE date >= now() - INTERVAL '{interval}'
      {and}
      GROUP BY iso)
  AS alerts ON alerts.iso = countries.iso
  ORDER BY countries.name {order}"""


RELATED_STORIES = """SELECT *, ST_Y(the_geom) || ',' || ST_X(the_geom) AS coordinates 
    FROM community_stories
    WHERE ST_contains(
        (SELECT the_geom FROM world_countries
         WHERE iso3='{iso}' LIMIT 1),the_geom)"""


def has_alerts(params):
    return json.loads(
        cdb.execute(
            HAS_ALERTS.format(**params)).content)['rows'][0]['count'] != 0


def get(params):
    if not 'order' in params:
        params['order'] = ''
    if 'iso' in params:
        params['and'] = "AND iso = upper('%s')" % params['iso']
        params['join'] = 'RIGHT'
        query = GET.format(**params)
    else:  # List all countries:
        params['and'] = ''
        params['join'] = 'LEFT'
        query = GET.format(**params)
    result = cdb.execute(query, params)
    if result:
        countries = json.loads(result.content)['rows']
        if countries and 'iso' in params:
            iso = params.get('iso').upper()
            query = RELATED_STORIES.format(iso=iso)
            story_result = cdb.execute(query)
            story = json.loads(story_result.content)['rows']
            if story:
                story = story[0]
                story['media'] = json.loads(story['media'])
                countries[0]['story'] = story
    return dict(countries=countries)
