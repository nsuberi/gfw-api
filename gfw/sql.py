FORMA_TABLE = 'forma_api'


FORMA_ANALYSIS = """
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
