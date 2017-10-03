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

from gfw.forestchange.common import Sql

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
