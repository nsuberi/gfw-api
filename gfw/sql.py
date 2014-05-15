FORMA_TABLE = 'forma_api'


FORMA_ANALYSIS = """
SELECT
   count(*) AS value
FROM
   %s forma
{where}""" % FORMA_TABLE


FORMA_ANALYSIS_GADM = """
SELECT   
   g.id_1,
   g.name_1,
   count(*) AS total
FROM
   forma_api t
INNER JOIN
   (
      SELECT
         *
      FROM
         gadm2
      WHERE
         {gadm_where}
   ) g
      ON t.gadm2::int=g.objectid
{where}
GROUP BY
   g.id_1,
   g.name_1
ORDER BY
   g.id_1
"""


# FORMA_ANALYSIS_GADM = """
# SELECT
#    count(*) AS value
# FROM
#    %s forma
# INNER JOIN
#    (
#       SELECT
#          gadm2.objectid id
#       FROM
#          gadm2
#       WHERE
#       {gadm_where}
#    ) gadm
#       ON forma.gadm2::int=gadm.id
# {where}""" % FORMA_TABLE


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
