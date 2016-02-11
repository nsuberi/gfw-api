forma_world = "SELECT COUNT(f.*) AS value FROM forma_api f WHERE f.date >= '2014-01-01'::date AND f.date <= '2015-01-01'::date AND ST_INTERSECTS( ST_SetSRID( ST_GeomFromGeoJSON('foo'), 4326), f.the_geom)"

forma_national = "SELECT COUNT(f.*) AS value FROM forma_api f WHERE f.date >= '2014-01-01'::date AND f.date <= '2015-01-01'::date AND f.iso = UPPER('bra')"

forma_subnational = "SELECT COUNT(f.*) AS value FROM forma_api f INNER JOIN ( SELECT * FROM gadm2 WHERE id_1 = 1 AND iso = UPPER('bra')) g ON f.gadm2::int = g.objectid WHERE f.date >= '2014-01-01'::date AND f.date <= '2015-01-01'::date"

forma_wdpa = "WITH p as (SELECT CASE when marine::numeric = 2 then null when ST_NPoints(the_geom)<=18000 THEN the_geom WHEN ST_NPoints(the_geom) BETWEEN 18000 AND 50000 THEN ST_RemoveRepeatedPoints(the_geom, 0.001) ELSE ST_RemoveRepeatedPoints(the_geom, 0.005) END as the_geom FROM wdpa_protected_areas where wdpaid=1) SELECT COUNT(f.*) AS value FROM forma_api f, p WHERE ST_Intersects(f.the_geom, p.the_geom) AND f.date >= '2014-01-01'::date AND f.date <= '2015-01-01'::date"

forma_use = "SELECT COUNT(f.*) AS value FROM gfw_logging u, forma_api f WHERE u.cartodb_id = 1 AND ST_Intersects(f.the_geom, u.the_geom) AND f.date >= '2014-01-01'::date AND f.date <= '2015-01-01'::date"

forma_begin = "SELECT COUNT(f.*) AS value FROM forma_api f WHERE f.date >= 'foo'::date AND f.date <= '2015-01-01'::date AND ST_INTERSECTS( ST_SetSRID( ST_GeomFromGeoJSON('foo'), 4326), f.the_geom)"

forma_end = "SELECT COUNT(f.*) AS value FROM forma_api f WHERE f.date >= '2014-01-01'::date AND f.date <= 'foo'::date AND ST_INTERSECTS( ST_SetSRID( ST_GeomFromGeoJSON('foo'), 4326), f.the_geom)"

forma_begin_end = "SELECT COUNT(f.*) AS value FROM forma_api f WHERE f.date >= 'foo'::date AND f.date <= 'foo'::date AND ST_INTERSECTS( ST_SetSRID( ST_GeomFromGeoJSON('foo'), 4326), f.the_geom)"
