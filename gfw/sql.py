FORMA_TABLE = 'forma_api'


FORMA_ANALYSIS = """
SELECT
   count(*) AS value
FROM
   %s forma
{where}""" % FORMA_TABLE


FORMA_ANALYSIS_GADM = """
SELECT
   count(*) AS value
FROM
   %s forma
INNER JOIN
   (
      SELECT
         gadm2.objectid id
      FROM
         gadm2
      {where}
   ) gadm
      ON forma.gadm2::int=gadm.id""" % FORMA_TABLE


FORMA_DOWNLOAD = """
SELECT
   forma.iso,
   forma.date,
   forma.lat,
   forma.lon
   {select}
FROM
   %s forma
INNER JOIN
   (
      SELECT
         gadm2.objectid id
      FROM
         gadm2
      {where}
   ) gadm
      ON forma.gadm2::int=gadm.id""" % FORMA_TABLE


FORMA_USE = """
SELECT
   count(forma.*) AS value
FROM
   {table} t,
   %s forma
{where}""" % FORMA_TABLE


QUICC_ANALYSIS = """
SELECT
   {select}
FROM
   modis_forest_change_copy t
{where}
"""

QUICC_ANALYSIS_GADM = """
SELECT
   {select}
FROM
   modis_forest_change_copy t,
   (SELECT
      *
   FROM
      gadm2
   {gadm_where}) as g
{where}
GROUP BY
  {group_by}
{order_by}
"""
