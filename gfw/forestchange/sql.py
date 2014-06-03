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

"""This module contains SQL helpers."""


class SqlError(ValueError):
    def __init__(self, msg):
        super(SqlError, self).__init__(msg)


class FormaSqlError(SqlError):
    PARAMS = """'begin' and 'end' dates in YYYY-MM-DD format"""

    def __init__(self):
        msg = 'Invalid SQL parameters for FORMA world query: %s' % \
            self.PARAMS
        super(FormaSqlError, self).__init__(msg)


class Sql():
    pass


class FormaSql(Sql):

    # Worldwide query with optional geojson filter:
    WORLD = """
        SELECT
           count(t.*) AS value
        FROM
           forma_api t
        WHERE
            date >= '{begin}'::date
            AND date <= '{end}'::date
            {geojson}"""

    # Worldwide download, optional the_geom (for non-csv) and geojson filter:
    WORLD_DOWNLOAD = """
        SELECT
           iso country_iso_code,
           to_char(date, 'YYYY-MM-DD') as year_month_day,
           lat,
           lon
           {the_geom}
        FROM
           forma_api t
        WHERE
            date >= '{begin}'::date
            AND date <= '{end}'::date
            {geojson}"""

    # Query by country:
    ISO = """
        SELECT
           t.iso,
           count(t.*) AS value
        FROM
           forma_api t
        WHERE
            date >= '{begin}'::date
            AND date <= '{end}'::date
            AND iso = UPPER('{iso}')
        GROUP BY
           t.iso"""

    # Query by country and administrative unit 1:
    ID1 = """
        SELECT
           g.id_1 AS id1,
           count(*) AS value
        FROM
           forma_api t
        INNER JOIN
           (
              SELECT
                 *
              FROM
                 gadm2
              WHERE
                 id_1 = {id1}
                 AND iso = UPPER('{iso}')
           ) g
              ON t.gadm2::int = g.objectid
        WHERE
           t.date >= '{begin}'::date
           AND t.date <= '{end}'::date
        GROUP BY
           id1
        ORDER BY
           id1"""

    # Query by concession use and concession polygon cartodb_id:
    USE = """
        SELECT
           u.cartodb_id AS pid,
           count(f.*) AS value
        FROM
           {use_table} u,
           forma_api f
        WHERE
           u.cartodb_id = {pid}
           AND ST_Intersects(f.the_geom, u.the_geom)
           AND f.date >= '{begin}'::date
           AND f.date <= '{end}'::date
        GROUP BY
           u.cartodb_id"""

    # Query by protected area:
    PA = """"""

    @classmethod
    def process(cls, args):
        begin = args['begin'] if 'begin' in args else '1969-01-01'
        end = args['end'] if 'end' in args else '3014-01-01'
        params = dict(begin=begin, end=end, geojson='', the_geom='')
        classification = cls.classify_query(args)
        if hasattr(cls, classification):
            return getattr(cls, classification)(params, args)

    @classmethod
    def world(cls, params, args):
        if 'geojson' in args:
            params['geojson'] = "AND ST_INTERSECTS(ST_SetSRID( \
                ST_GeomFromGeoJSON('%s'),4326),the_geom)" % args['geojson']
        return FormaSql.WORLD.format(**params)

    @classmethod
    def use(cls, params, args):
        concessions = {
            'mining': 'mining_permits_merge',
            'oilpalm': 'oil_palm_permits_merge',
            'fiber': 'fiber_all_merged',
            'logging': 'logging_all_merged'
        }
        params['use_table'] = concessions[args['use']]
        params['pid'] = args['use_pid']
        return FormaSql.USE.format(**params)

    @classmethod
    def iso(cls, params, args):
        params['iso'] = args['iso']
        return FormaSql.ISO.format(**params)

    @classmethod
    def id1(cls, params, args):
        params['iso'] = args['iso']
        params['id1'] = args['id1']
        return FormaSql.ID1.format(**params)

    @classmethod
    def world_download(cls, params, args):
        if 'geojson' in args:
            params['geojson'] = "AND ST_INTERSECTS(ST_SetSRID( \
                ST_GeomFromGeoJSON('%s'),4326),the_geom)" % args['geojson']
        if args['format'] != 'csv':
            params['the_geom'] = ', the_geom'
        return FormaSql.WORLD_DOWNLOAD.format(**params)

    @classmethod
    def classify_query(cls, args):
        if 'iso' in args and not 'id1' in args:
            return 'iso'
        elif 'iso' in args and 'id1' in args:
            return 'id1'
        elif 'use' in args:
            return 'use'
        elif 'pa' in args:
            return 'pa'
        else:
            if 'format' in args:
                return 'world_download'
            else:
                return 'world'
