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


class Sql(object):

    @classmethod
    def get_query_type(cls, params, args, the_geom_table=''):
        """Return query type (download or analysis) with updated params."""
        query_type = 'analysis'
        if 'format' in args:
            query_type = 'download'
            if args['format'] != 'csv':
                the_geom = ', the_geom' \
                    if not the_geom_table \
                    else ', %s.the_geom' % the_geom_table
                params['the_geom'] = the_geom
        return query_type, params

    @classmethod
    def process(cls, args):
        begin = args['begin'] if 'begin' in args else '1969-01-01'
        end = args['end'] if 'end' in args else '3014-01-01'
        params = dict(begin=begin, end=end, geojson='', the_geom='')
        classification = cls.classify_query(args)
        if hasattr(cls, classification):
            return getattr(cls, classification)(params, args)

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
        elif 'wdpaid' in args:
            return 'wdpa'
        else:
            return 'world'


class FiresSql(Sql):

    # Worldwide query
    WORLD = """
        SELECT
           count(pt.*) AS value
        FROM
           global_7d pt
        WHERE
           acq_date >= '{begin}'::date
           AND acq_date <= '{end}'::date
           {geojson}"""

    # Worldwide download
    # WORLD_DOWNLOAD = """
    #     SELECT
    #        iso country_iso_code,
    #        to_char(date, 'YYYY-MM-DD') as year_month_day,
    #        lat,
    #        lon
    #        {the_geom}
    #     FROM
    #        forma_api t
    #     WHERE
    #         date >= '{begin}'::date
    #         AND date <= '{end}'::date
    #         {geojson}"""

    # Query by country:
    ISO = """
        SELECT
           p.iso,
           count(pt.*) AS value
        FROM
           global_7d pt,
           (SELECT
              *
           FROM
              gadm2
           WHERE
              iso=UPPER('{iso}')) as p
        WHERE
           ST_Intersects(pt.the_geom, p.the_geom)
           AND acq_date >= '{begin}'::date
           AND acq_date <= '{end}'::date
        GROUP BY
           p.iso"""

    # Download query by country:
    # ISO_DOWNLOAD = """
    #     SELECT
    #        iso country_iso_code,
    #        to_char(date, 'YYYY-MM-DD') as year_month_day,
    #        lat,
    #        lon
    #        {the_geom}
    #     FROM
    #        forma_api t
    #     WHERE
    #         date >= '{begin}'::date
    #         AND date <= '{end}'::date
    #         AND iso = UPPER('{iso}')
    #     GROUP BY
    #        t.iso,
    #        t.date,
    #        t.lat,
    #        t.lon,
    #        t.the_geom"""

    # Query by country and administrative unit 1:

    ID1 = """
        SELECT
           p.id_1 AS id1,
           p.iso AS iso,
           count(pt.*) AS value
        FROM
           global_7d pt,
           (SELECT
              *
           FROM
              gadm2
           WHERE
              iso=UPPER('{iso}')
              AND id_1={id1}) as p
        WHERE
           ST_Intersects(pt.the_geom, p.the_geom)
           AND acq_date::date >= '{begin}'::date
           AND acq_date::date <= '{end}'::date
        GROUP BY
           p.id_1,
           p.iso
        ORDER BY
           p.id_1"""

    # Download by country and administrative unit 1:
    # ID1_DOWNLOAD = """
    #     SELECT
    #        g.id_1 AS id1,
    #        t.iso country_iso_code,
    #        to_char(date, 'YYYY-MM-DD') as year_month_day,
    #        lat,
    #        lon
    #        {the_geom}
    #     FROM
    #        forma_api t
    #     INNER JOIN
    #        (
    #           SELECT
    #              *
    #           FROM
    #              gadm2
    #           WHERE
    #              id_1 = {id1}
    #              AND iso = UPPER('{iso}')
    #        ) g
    #           ON t.gadm2::int = g.objectid
    #     WHERE
    #        t.date >= '{begin}'::date
    #        AND t.date <= '{end}'::date
    #     GROUP BY
    #        id1,
    #        t.iso,
    #        t.date,
    #        t.lat,
    #        t.lon,
    #        t.the_geom
    #     ORDER BY
    #        id1"""

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

    # Query by concession use and concession polygon cartodb_id:
    USE_DOWNLOAD = """
        SELECT
           u.cartodb_id AS pid,
           f.iso country_iso_code,
           to_char(f.date, 'YYYY-MM-DD') as year_month_day,
           f.lat,
           f.lon
           {the_geom}
        FROM
           {use_table} u,
           forma_api f
        WHERE
           u.cartodb_id = {pid}
           AND ST_Intersects(f.the_geom, u.the_geom)
           AND f.date >= '{begin}'::date
           AND f.date <= '{end}'::date
        GROUP BY
           u.cartodb_id,
           f.iso,
           f.date,
           f.lat,
           f.lon,
           f.the_geom"""

    # Query by protected area:
    WDPA = """
        SELECT
           p.wdpaid,
           count(f.*) AS value
        FROM
           forma_api f,
           (SELECT
              *
           FROM
              wdpa_all
           WHERE
              wdpaid={wdpaid}) AS p
        WHERE
           ST_Intersects(f.the_geom, p.the_geom)
           AND f.date >= '{begin}'::date
           AND f.date <= '{end}'::date
        GROUP BY
           p.wdpaid
        ORDER BY
           p.wdpaid"""

    # Query by protected area:
    WDPA_DOWNLOAD = """
        SELECT
           p.wdpaid,
           f.iso country_iso_code,
           to_char(f.date, 'YYYY-MM-DD') as year_month_day,
           f.lat,
           f.lon
           {the_geom}
        FROM
           forma_api f,
           (SELECT
              *
           FROM
              wdpa_all
           WHERE
              wdpaid={wdpaid}) AS p
        WHERE
           ST_Intersects(f.the_geom, p.the_geom)
           AND f.date >= '{begin}'::date
           AND f.date <= '{end}'::date
        GROUP BY
           p.wdpaid,
           f.iso,
           f.date,
           f.lat,
           f.lon,
           f.the_geom
        ORDER BY
           p.wdpaid"""

    @classmethod
    def get_query_type(cls, params, args, the_geom_table=''):
        """Return query type (download or analysis) with updated params."""
        query_type = 'analysis'
        if 'format' in args:
            query_type = 'download'
            if args['format'] != 'csv':
                the_geom = ', the_geom' \
                    if not the_geom_table \
                    else ', %s.the_geom' % the_geom_table
                params['the_geom'] = the_geom
        return query_type, params

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
        query_type, params = cls.get_query_type(params, args)
        if query_type == 'download':
            return cls.WORLD_DOWNLOAD.format(**params)
        else:
            return cls.WORLD.format(**params)

    @classmethod
    def use(cls, params, args):
        concessions = {
            'mining': 'mining_permits_merge',
            'oilpalm': 'oil_palm_permits_merge',
            'fiber': 'fiber_all_merged',
            'logging': 'logging_all_merged'
        }
        params['use_table'] = concessions[args['use']]
        params['pid'] = args['useid']
        query_type, params = cls.get_query_type(
            params, args, the_geom_table='f')
        if query_type == 'download':
            return cls.USE_DOWNLOAD.format(**params)
        else:
            return cls.USE.format(**params)

    @classmethod
    def iso(cls, params, args):
        params['iso'] = args['iso']
        query_type, params = cls.get_query_type(params, args)
        if query_type == 'download':
            return cls.ISO_DOWNLOAD.format(**params)
        else:
            return cls.ISO.format(**params)

    @classmethod
    def id1(cls, params, args):
        params['iso'] = args['iso']
        params['id1'] = args['id1']
        query_type, params = cls.get_query_type(
            params, args, the_geom_table='pt')
        if query_type == 'download':
            return cls.ID1_DOWNLOAD.format(**params)
        else:
            return cls.ID1.format(**params)

    @classmethod
    def wdpa(cls, params, args):
        params['wdpaid'] = args['wdpaid']
        query_type, params = cls.get_query_type(
            params, args, the_geom_table='f')
        if query_type == 'download':
            return cls.WDPA_DOWNLOAD.format(**params)
        else:
            return cls.WDPA.format(**params)

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
        elif 'wdpaid' in args:
            return 'wdpa'
        else:
            return 'world'





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

    # Download query by country:
    ISO_DOWNLOAD = """
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
            AND iso = UPPER('{iso}')
        GROUP BY
           t.iso,
           t.date,
           t.lat,
           t.lon,
           t.the_geom"""

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

    # Download by country and administrative unit 1:
    ID1_DOWNLOAD = """
        SELECT
           g.id_1 AS id1,
           t.iso country_iso_code,
           to_char(date, 'YYYY-MM-DD') as year_month_day,
           lat,
           lon
           {the_geom}
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
           id1,
           t.iso,
           t.date,
           t.lat,
           t.lon,
           t.the_geom
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

    # Query by concession use and concession polygon cartodb_id:
    USE_DOWNLOAD = """
        SELECT
           u.cartodb_id AS pid,
           f.iso country_iso_code,
           to_char(f.date, 'YYYY-MM-DD') as year_month_day,
           f.lat,
           f.lon
           {the_geom}
        FROM
           {use_table} u,
           forma_api f
        WHERE
           u.cartodb_id = {pid}
           AND ST_Intersects(f.the_geom, u.the_geom)
           AND f.date >= '{begin}'::date
           AND f.date <= '{end}'::date
        GROUP BY
           u.cartodb_id,
           f.iso,
           f.date,
           f.lat,
           f.lon,
           f.the_geom"""

    # Query by protected area:
    WDPA = """
        SELECT
           p.wdpaid,
           count(f.*) AS value
        FROM
           forma_api f,
           (SELECT
              *
           FROM
              wdpa_all
           WHERE
              wdpaid={wdpaid}) AS p
        WHERE
           ST_Intersects(f.the_geom, p.the_geom)
           AND f.date >= '{begin}'::date
           AND f.date <= '{end}'::date
        GROUP BY
           p.wdpaid
        ORDER BY
           p.wdpaid"""

    # Query by protected area:
    WDPA_DOWNLOAD = """
        SELECT
           p.wdpaid,
           f.iso country_iso_code,
           to_char(f.date, 'YYYY-MM-DD') as year_month_day,
           f.lat,
           f.lon
           {the_geom}
        FROM
           forma_api f,
           (SELECT
              *
           FROM
              wdpa_all
           WHERE
              wdpaid={wdpaid}) AS p
        WHERE
           ST_Intersects(f.the_geom, p.the_geom)
           AND f.date >= '{begin}'::date
           AND f.date <= '{end}'::date
        GROUP BY
           p.wdpaid,
           f.iso,
           f.date,
           f.lat,
           f.lon,
           f.the_geom
        ORDER BY
           p.wdpaid"""

    @classmethod
    def get_query_type(cls, params, args, the_geom_table=''):
        """Return query type (download or analysis) with updated params."""
        query_type = 'analysis'
        if 'format' in args:
            query_type = 'download'
            if args['format'] != 'csv':
                the_geom = ', the_geom' \
                    if not the_geom_table \
                    else ', %s.the_geom' % the_geom_table
                params['the_geom'] = the_geom
        return query_type, params

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
        query_type, params = cls.get_query_type(params, args)
        if query_type == 'download':
            return cls.WORLD_DOWNLOAD.format(**params)
        else:
            return cls.WORLD.format(**params)

    @classmethod
    def use(cls, params, args):
        concessions = {
            'mining': 'mining_permits_merge',
            'oilpalm': 'oil_palm_permits_merge',
            'fiber': 'fiber_all_merged',
            'logging': 'logging_all_merged'
        }
        params['use_table'] = concessions[args['use']]
        params['pid'] = args['useid']
        query_type, params = cls.get_query_type(
            params, args, the_geom_table='f')
        if query_type == 'download':
            return cls.USE_DOWNLOAD.format(**params)
        else:
            return cls.USE.format(**params)

    @classmethod
    def iso(cls, params, args):
        params['iso'] = args['iso']
        query_type, params = cls.get_query_type(params, args)
        if query_type == 'download':
            return cls.ISO_DOWNLOAD.format(**params)
        else:
            return cls.ISO.format(**params)

    @classmethod
    def id1(cls, params, args):
        params['iso'] = args['iso']
        params['id1'] = args['id1']
        query_type, params = cls.get_query_type(
            params, args, the_geom_table='t')
        if query_type == 'download':
            return cls.ID1_DOWNLOAD.format(**params)
        else:
            return cls.ID1.format(**params)

    @classmethod
    def wdpa(cls, params, args):
        params['wdpaid'] = args['wdpaid']
        query_type, params = cls.get_query_type(
            params, args, the_geom_table='f')
        if query_type == 'download':
            return cls.WDPA_DOWNLOAD.format(**params)
        else:
            return cls.WDPA.format(**params)

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
        elif 'wdpaid' in args:
            return 'wdpa'
        else:
            return 'world'
