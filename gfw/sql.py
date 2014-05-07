FORMA_TABLE = 'forma_api'


FORMA_ANALYSIS = """
SELECT SUM(COUNT) AS value
FROM
  (SELECT COUNT(*), iso, date
   FROM %s
   WHERE
     {location}
     AND date >= '{begin}'
     AND date <= '{end}'
   GROUP BY date, iso
   ORDER BY iso, date) AS ALIAS""" % FORMA_TABLE


FORMA_DOWNLOAD = """
SELECT iso country_iso_code,
       to_char(date, 'YYYY-MM-DD') AS year_month_day,
       lat,
       lon {select}
FROM %s
WHERE
  {location}
  AND date >= '{begin}'
  AND date <= '{end}'""" % FORMA_TABLE
