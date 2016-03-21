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

"""This module supports accessing countries data. todo- add loss outside plantations to umd"""

import json

from gfw import cdb
from gfw.forestchange import umd
from gfw import stories

class CountrySql(object):

    INDEX = """
        SELECT countries.iso, countries.name, countries.enabled, countries.lat,
        countries.lng, countries.extent, countries.gva, countries.gva_percent,
        countries.employment, countries.indepth, countries.national_policy_link,
        countries.national_policy_title, countries.convention_cbd,
        countries.convention_unfccc, countries.convention_kyoto,
        countries.convention_unccd, countries.convention_itta,
        countries.convention_cites, countries.convention_ramsar,
        countries.convention_world_heritage, countries.convention_nlbi,
        countries.convention_ilo, countries.ministry_link, countries.external_links,
        countries.dataset_link, countries.emissions, countries.carbon_stocks,
        countries.country_alt, alerts.count AS alerts_count
        FROM gfw2_countries AS countries
        LEFT OUTER JOIN (
          SELECT COUNT(*) AS count, iso
          FROM forma_api
          WHERE date >= now() - INTERVAL '{interval}'
          GROUP BY iso)
        AS alerts ON alerts.iso = countries.iso
        ORDER BY countries.name {order}
    """

    SHOW = """
        SELECT countries.iso, countries.name, countries.enabled, countries.lat,
        countries.lng, countries.extent, countries.gva, countries.gva_percent,
        countries.employment, countries.indepth, countries.national_policy_link,
        countries.national_policy_title, countries.convention_cbd,
        countries.convention_unfccc, countries.convention_kyoto,
        countries.convention_unccd, countries.convention_itta,
        countries.convention_cites, countries.convention_ramsar,
        countries.convention_world_heritage, countries.convention_nlbi,
        countries.convention_ilo, countries.ministry_link, countries.external_links,
        countries.dataset_link, countries.emissions, countries.carbon_stocks,
        countries.country_alt
        FROM gfw2_countries AS countries
        WHERE countries.iso = UPPER('{iso}')
        LIMIT 1
    """

    TOPO_JSON = """
        SELECT the_geom
        FROM forest_cov_glob_v3
        WHERE country_code = UPPER('{iso}')
        UNION
        SELECT the_geom
        FROM ne_50m_admin_0_countries
        WHERE adm0_a3 = UPPER('{iso}')"""

    SUBNAT_BOUNDS = """
        SELECT cartodb_id, iso, id_1, name_1, bounds
        FROM gadm_1_all
        WHERE iso = UPPER('{iso}')
        ORDER BY id_1 asc"""

    TENURE = """
        SELECT tenure_government, tenure_owned, tenure_owned_individuals,
            tenure_reserved, GREATEST(tenure_government, tenure_owned,
            tenure_owned_individuals, tenure_owned_individuals,
            tenure_reserved) AS max
        FROM gfw2_countries
        WHERE iso = UPPER('{iso}')"""

    FORESTS = """
        SELECT unnest(array['forest_regenerated', 'forest_primary',
               'forest_planted']) AS type, unnest(array[COALESCE(
               forest_regenerated, 0), COALESCE(forest_primary, 0), COALESCE(
               forest_planted, 0)]) AS percent
        FROM gfw2_countries
        WHERE iso = UPPER('{iso}')"""

    FORMA = """
        SELECT date_trunc('month', date) AS date, COUNT(*) AS alerts
        FROM forma_api
        WHERE iso = UPPER('{iso}')
        GROUP BY date_trunc('month', date)
        ORDER BY date_trunc('month', date) ASC"""

    BOUNDS = """
        SELECT bounds
        FROM country_mask
        WHERE code = UPPER('{iso}')"""

    BURNED_FOREST = """
        SELECT area_burned_forest, year
        FROM burned_forest
        WHERE iso = UPPER('{iso}')
        ORDER BY year asc"""

    REFORESTATION = """
        SELECT reforestation_rate
        FROM gfw2_countries
        WHERE iso = UPPER('{iso}')"""

    FOREST_CERTIFICATION = """
        SELECT unnest(array['total_area_certified', 'percent_fsc',
               'percent_pef','percent_other']) AS type, unnest(array[COALESCE(
               total_area_certified, 0), COALESCE(percent_fsc, 0), COALESCE(
               percent_pef, 0), COALESCE(percent_other, 0)]) AS value
        FROM gfw2_countries
        WHERE iso = UPPER('{iso}')"""

    LOSS_OUTSIDE_PLANTATION = """
        select loss_outside,perc_loss_outside,iso, threshold, year 
        FROM loss_outside_plantations
        WHERE iso = UPPER('{iso}')
        AND threshold = {thresh}
        AND year > 2012
        ORDER BY year asc"""


def _handler(response):
    if response.status_code == 200:
        data = json.loads(response.content)
        if 'rows' in data:
            return data['rows']
        else:
            return data
    else:
        raise Exception(response.content)


def _index(args):
    if not 'order' in args:
        args['order'] = ''
    if not 'interval' in args:
        args['interval'] = '12 Months'
    query = CountrySql.INDEX.format(**args)
    rows = _handler(cdb.execute(query))
    return dict(countries=rows)

def _show(args):
    query = CountrySql.SHOW.format(**args)
    rows = _handler(cdb.execute(query))
    return rows[0]

def _getTopoJson(args):
    query = CountrySql.TOPO_JSON.format(**args)

    rows = _handler(
        cdb.execute(query, params=dict(format='topojson')))
    return dict(topojson=rows)

def _processSubnatRow(x):
    x['bounds'] = json.loads(x['bounds'])
    return x


def _getSubnatBounds(args):
    query = CountrySql.SUBNAT_BOUNDS.format(**args)

    rows = _handler(cdb.execute(query))
    results = map(_processSubnatRow, rows)
    return dict(subnat_bounds=results)


def _getForma(args):
    query = CountrySql.FORMA.format(**args)

    return dict(forma=_handler(cdb.execute(query)))


def _getForests(args):
    query = CountrySql.FORESTS.format(**args)

    return dict(forests=_handler(cdb.execute(query)))


def _getTenure(args):
    query = CountrySql.TENURE.format(**args)

    return dict(tenure=_handler(cdb.execute(query)))


def _getBurnedForests(args):
    query = CountrySql.BURNED_FOREST.format(**args)

    return dict(burned_forests=_handler(cdb.execute(query)))

def _getReforestation(args):
    query = CountrySql.REFORESTATION.format(**args)

    return dict(reforestation=_handler(cdb.execute(query)))

def _getForestCertification(args):
    query = CountrySql.FOREST_CERTIFICATION.format(**args)

    return dict(forest_certification=_handler(cdb.execute(query)))

def _getLossOutsidePlantations(args):
    if 'thresh' not in args:
        args['thresh'] = 30
    query = CountrySql.LOSS_OUTSIDE_PLANTATION.format(**args)

    return dict(loss_outside_plantations=_handler(cdb.execute(query)))

def _getBounds(args):
    query = CountrySql.BOUNDS.format(**args)

    return dict(bounds=json.loads(_handler(cdb.execute(query))[0]['bounds']))

def _getstory(args):
    return dict(story=stories.get_country_story(args))

def _getUmd(args):
    action, data = umd.execute(args)

    return dict(umd=data['years'])

def _getIfl(args):
    args['ifl'] = True
    ifl = umd.execute(args)
    args['ifl'] = False
        
    return dict(ifl=ifl)

def execute(args):
    result = dict(params=args)

    if args.get('index'):
        result.update(_index(args))

    else:
        result.update(_show(args))
        result.update(_getTopoJson(args))
        result.update(_getSubnatBounds(args))
        result.update(_getForma(args))
        result.update(_getForests(args))
        result.update(_getTenure(args))
        result.update(_getBurnedForests(args))
        result.update(_getReforestation(args))
        result.update(_getForestCertification(args))
        result.update(_getLossOutsidePlantations(args))
        result.update(_getBounds(args))
        result.update(_getUmd(args))
        result.update(_getIfl(args))
        result.update(_getstory(args))

    return 'respond', result
