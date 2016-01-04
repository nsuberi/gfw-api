[![Build Status](https://travis-ci.org/wri/gfw-api.svg?branch=feature%2Fv1)](https://travis-ci.org/wri/gfw-api) [![Code Health](https://landscape.io/github/wri/gfw-api/feature/v1/landscape.png)](https://landscape.io/github/wri/gfw-api/feature/v1)

[1]: http://www.geog.umd.edu/                      "UMD Geographical Sciences Department"
[2]: http://www.cgdev.org/                         "FORMA"
[3]: http://imazon.org.br/                         "IMAZON"
[4]: http://geo.arc.nasa.gov/sge/casa/latest.html  "QUICC"
[5]: http://www.terra-i.org/                       "TERRA-I"
[6]: https://earthdata.nasa.gov/earth-observation-data/near-real-time/firms/active-fire-data "NASA Active Fires"
[7]: http://www.iso.org/iso/country_codes        "ISO Country Codes"
[8]: http://geojson.org/geojson-spec.html#id4      "geoJSON Polygon structure"
[9]: http://geojson.org/geojson-spec.html#id7      "geoJSON MultiPolygon structure"

# API Overview

The Global Forest Watch API is currently in beta. Based on feedback from trusted testers, this document specifies new API changes that are currently under development. Interested in being a trusted tester? Contact the Data Lab (datalab@wri.org) at World Resources Institute. 

# Forest Change API

Forest change measures tree cover loss, tree cover gain, or forest disturbance. The following forest change data are available through the API: [University of Maryland][1] tree cover loss & gain, [FORMA][2] alerts, [IMAZON SAD][3] alerts, [QUICC][4] alerts, [TERRA-I][5] alerts, and [NASA active fires][6].


The following API calls require one of the following datasets (:dataset) as a url parameter:

* umd-loss-gain
* forma-alerts
* imazon-alerts
* quicc-alerts
* terrai-alerts
* nasa-active-fires

## Geometry

Returns alerts which lie within a passed geoJSON polygon or multi-polygon.

```GET http://api.globalforestwatch.org/forest-change/:dataset```

**PARAMETERS**

Parameter | Required | Description
--------- | -------- | -----------
geojson | true | GeoJSON encoded Polygon or MultiPolygon (as described [here][8] and [here][9]) for calculating alerts within their area. Note that this parameter is ignored if your request includes the [ISO Country Code][7] and/or `ID1` parameters in the request path. 
period | false | Period of interest, as comma separated begin and end dates, inclusive. Dates are in YYYY-MM-DD format. Examples: `period=2006-10-08,2008-10-01` for an alert count between 2006-10-08 and 2008-10-01 inclusive, or `period=2008-10-01,2008-10-01` for an alert count for 2008-10-01
download | false | Filename: filename.{csv \| kml \| shp \| geojson \| svg}. If provided the response will be downloaded to a file rather than displayed as html. File type is determined by the filename extension.
dev | false | If exists in query string the returned JSON will include the SQL query
bust | false | If exists in query string the results will be processed even if they have previously been cached 

**EXAMPLE**

```POST http://api.globalforestwatch.org/forest-change/forma-alerts```

**PAYLOAD**
```
{"geojson":'{"type":"Polygon","coordinates":[[[12.8,8.9],[13.3,-7.3],[32.5,-6.6],[32.5,7.7],[12.8,8.9]]]}'}
```

**RESPONSE**

```json
{  
   "apis":{  
      "national":"http://api.globalforestwatch.org/forma-alerts/admin{/iso}{?period,download,bust,dev}",
      "subnational":"http://api.globalforestwatch.org/forma-alerts/admin{/iso}{/id1}{?period,download,bust,dev}",
      "use":"http://api.globalforestwatch.org/forma-alerts/use/{/name}{/id}{?period,download,bust,dev}",
      "wdpa":"http://api.globalforestwatch.org/forma-alerts/wdpa/{/id}{?period,download,bust,dev}",
      "world":"http://api.globalforestwatch.org/forma-alerts{?period,geojson,download,bust,dev}"
   },
   "download_urls":{  
      "csv":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f+WHERE+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate+AND+ST_INTERSECTS%28+ST_SetSRID%28+ST_GeomFromGeoJSON%28%27%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B12.832%2C8.9285%5D%2C%5B13.3594%2C-7.3625%5D%2C%5B32.5195%2C-6.6646%5D%2C%5B32.5195%2C7.711%5D%2C%5B12.832%2C8.9285%5D%5D%5D%7D%27%29%2C+4326%29%2C+f.the_geom%29&version=v1&format=csv",
      "geojson":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f+WHERE+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate+AND+ST_INTERSECTS%28+ST_SetSRID%28+ST_GeomFromGeoJSON%28%27%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B12.832%2C8.9285%5D%2C%5B13.3594%2C-7.3625%5D%2C%5B32.5195%2C-6.6646%5D%2C%5B32.5195%2C7.711%5D%2C%5B12.832%2C8.9285%5D%5D%5D%7D%27%29%2C+4326%29%2C+f.the_geom%29&version=v1&format=geojson",
      "kml":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f+WHERE+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate+AND+ST_INTERSECTS%28+ST_SetSRID%28+ST_GeomFromGeoJSON%28%27%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B12.832%2C8.9285%5D%2C%5B13.3594%2C-7.3625%5D%2C%5B32.5195%2C-6.6646%5D%2C%5B32.5195%2C7.711%5D%2C%5B12.832%2C8.9285%5D%5D%5D%7D%27%29%2C+4326%29%2C+f.the_geom%29&version=v1&format=kml",
      "shp":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f+WHERE+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate+AND+ST_INTERSECTS%28+ST_SetSRID%28+ST_GeomFromGeoJSON%28%27%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B12.832%2C8.9285%5D%2C%5B13.3594%2C-7.3625%5D%2C%5B32.5195%2C-6.6646%5D%2C%5B32.5195%2C7.711%5D%2C%5B12.832%2C8.9285%5D%5D%5D%7D%27%29%2C+4326%29%2C+f.the_geom%29&version=v1&format=shp",
      "svg":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f+WHERE+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate+AND+ST_INTERSECTS%28+ST_SetSRID%28+ST_GeomFromGeoJSON%28%27%7B%22type%22%3A%22Polygon%22%2C%22coordinates%22%3A%5B%5B%5B12.832%2C8.9285%5D%2C%5B13.3594%2C-7.3625%5D%2C%5B32.5195%2C-6.6646%5D%2C%5B32.5195%2C7.711%5D%2C%5B12.832%2C8.9285%5D%5D%5D%7D%27%29%2C+4326%29%2C+f.the_geom%29&version=v1&format=svg"
   },
   "max_date":null,
   "meta":{  
      "coverage":"Humid tropical forest biome",
      "description":"Forest disturbances alerts.",
      "id":"forma-alerts",
      "name":"FORMA Alerts",
      "resolution":"500 x 500 meters",
      "source":"MODIS",
      "timescale":"January 2006 to present",
      "units":"Alerts",
      "updates":"16 day"
   },
   "min_date":null,
   "params":{  
      "geojson":{  
         "coordinates":[  
            [  
               [  
                  12.832000000000001,
                  8.9284999999999997
               ],
               [  
                  13.359400000000001,
                  -7.3624999999999998
               ],
               [  
                  32.519500000000001,
                  -6.6646000000000001
               ],
               [  
                  32.519500000000001,
                  7.7110000000000003
               ],
               [  
                  12.832000000000001,
                  8.9284999999999997
               ]
            ]
         ],
         "type":"Polygon"
      },
      "version":"v1"
   },
   "value":7855
}
```

## National & Subnational

Returns alerts which lie within national (given by [ISO Country Code][7]) or subnational (given by ID1) boundaries. 

```GET http://api.globalforestwatch.org/forest-change/:dataset/admin/:iso(/:id1)```

**PARAMETERS**

Parameter | Required | Description
--------- | -------- | -----------
period | false | Period of interest, as comma separated begin and end dates, inclusive. Dates are in YYYY-MM-DD format. Examples: `period=2006-10-08,2008-10-01` for an alert count between 2006-10-08 and 2008-10-01 inclusive, or `period=2008-10-01,2008-10-01` for an alert count for 2008-10-01
download | false | Filename: filename.{csv \| kml \| shp \| geojson \| svg}. If provided the response will be downloaded to a file rather than displayed as html. File type is determined by the filename extension.
dev | false | If exists in query string the returned JSON will include the SQL query
bust | false | If exists in query string the results will be processed even if they have previously been cached 

**EXAMPLE**

http://api.globalforestwatch.org/forest-change/terrai-alerts/admin/bra?period=2012-01-01,2015-01-01

**RESPONSE**

```json
{  
   "apis":{  
      "national":"http://api.globalforestwatch.org/terrai-alerts/admin{/iso}{?period,download,bust,dev}",
      "subnational":"http://api.globalforestwatch.org/terrai-alerts/admin{/iso}{/id1}{?period,download,bust,dev}",
      "use":"http://api.globalforestwatch.org/terrai-alerts/use/{/name}{/id}{?period,download,bust,dev}",
      "wdpa":"http://api.globalforestwatch.org/terrai-alerts/wdpa/{/id}{?period,download,bust,dev}",
      "world":"http://api.globalforestwatch.org/terrai-alerts{?period,geojson,download,bust,dev}"
   },
   "download_urls":{  
      "csv":"http://wri-01.cartodb.com/api/v2/sql?q=SELECT+COUNT%28f.%2A%29+AS+value+FROM+latin_decrease_current_points+f+WHERE+iso+%3D+UPPER%28%27bra%27%29+AND+date+%3E%3D+%272012-01-01%27%3A%3Adate+AND+date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v2&format=csv",
      "geojson":"http://wri-01.cartodb.com/api/v2/sql?q=SELECT+COUNT%28f.%2A%29+AS+value+FROM+latin_decrease_current_points+f+WHERE+iso+%3D+UPPER%28%27bra%27%29+AND+date+%3E%3D+%272012-01-01%27%3A%3Adate+AND+date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v2&format=geojson",
      "kml":"http://wri-01.cartodb.com/api/v2/sql?q=SELECT+COUNT%28f.%2A%29+AS+value+FROM+latin_decrease_current_points+f+WHERE+iso+%3D+UPPER%28%27bra%27%29+AND+date+%3E%3D+%272012-01-01%27%3A%3Adate+AND+date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v2&format=kml",
      "shp":"http://wri-01.cartodb.com/api/v2/sql?q=SELECT+COUNT%28f.%2A%29+AS+value+FROM+latin_decrease_current_points+f+WHERE+iso+%3D+UPPER%28%27bra%27%29+AND+date+%3E%3D+%272012-01-01%27%3A%3Adate+AND+date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v2&format=shp",
      "svg":"http://wri-01.cartodb.com/api/v2/sql?q=SELECT+COUNT%28f.%2A%29+AS+value+FROM+latin_decrease_current_points+f+WHERE+iso+%3D+UPPER%28%27bra%27%29+AND+date+%3E%3D+%272012-01-01%27%3A%3Adate+AND+date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v2&format=svg"
   },
   "max_date":null,
   "meta":{  
      "coverage":"Latin America",
      "description":"Forest decrease alerts.",
      "id":"terrai-alerts",
      "name":"Terra-i Alerts",
      "resolution":"250 x 250 meters",
      "source":"MODIS",
      "timescale":"January 2004 to present",
      "units":"Alerts",
      "updates":"16 day"
   },
   "min_date":null,
   "params":{  
      "begin":"2012-01-01",
      "end":"2015-01-01",
      "iso":"bra",
      "version":"v2"
   },
   "value":446662
}
```


## World Database on Protected Areas (WDPA)

Returns alerts which lie within a given protected area.

```GET http://api.globalforestwatch.org/forest-change/:dataset/wdpa/:wdpa```

**PARAMETERS**

Parameter | Required | Description
--------- | -------- | -----------
period | false | Period of interest, as comma separated begin and end dates, inclusive. Dates are in YYYY-MM-DD format. Examples: `period=2006-10-08,2008-10-01` for an alert count between 2006-10-08 and 2008-10-01 inclusive, or `period=2008-10-01,2008-10-01` for an alert count for 2008-10-01
download | false | Filename: filename.{csv \| kml \| shp \| geojson \| svg}. If provided the response will be downloaded to a file rather than displayed as html. File type is determined by the filename extension.
dev | false | If exists in query string the returned JSON will include the SQL query
bust | false | If exists in query string the results will be processed even if they have previously been cached 

**EXAMPLE**

http://api.globalforestwatch.org/forest-change/forma-alerts/wdpa/8950

**RESPONSE**

```json
{  
   "apis":{  
      "national":"http://api.globalforestwatch.org/forma-alerts/admin{/iso}{?period,download,bust,dev}",
      "subnational":"http://api.globalforestwatch.org/forma-alerts/admin{/iso}{/id1}{?period,download,bust,dev}",
      "use":"http://api.globalforestwatch.org/forma-alerts/use/{/name}{/id}{?period,download,bust,dev}",
      "wdpa":"http://api.globalforestwatch.org/forma-alerts/wdpa/{/id}{?period,download,bust,dev}",
      "world":"http://api.globalforestwatch.org/forma-alerts{?period,geojson,download,bust,dev}"
   },
   "download_urls":{  
      "csv":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f%2C+%28SELECT+%2A+FROM+protected_areas+WHERE+wdpaid%3D8950%29+AS+p+WHERE+ST_Intersects%28f.the_geom%2C+p.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=csv",
      "geojson":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f%2C+%28SELECT+%2A+FROM+protected_areas+WHERE+wdpaid%3D8950%29+AS+p+WHERE+ST_Intersects%28f.the_geom%2C+p.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=geojson",
      "kml":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f%2C+%28SELECT+%2A+FROM+protected_areas+WHERE+wdpaid%3D8950%29+AS+p+WHERE+ST_Intersects%28f.the_geom%2C+p.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=kml",
      "shp":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f%2C+%28SELECT+%2A+FROM+protected_areas+WHERE+wdpaid%3D8950%29+AS+p+WHERE+ST_Intersects%28f.the_geom%2C+p.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=shp",
      "svg":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+forma_api+f%2C+%28SELECT+%2A+FROM+protected_areas+WHERE+wdpaid%3D8950%29+AS+p+WHERE+ST_Intersects%28f.the_geom%2C+p.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=svg"
   },
   "meta":{  
      "coverage":"Humid tropical forest biome",
      "description":"Forest disturbances alerts.",
      "id":"forma-alerts",
      "name":"FORMA Alerts",
      "resolution":"500 x 500 meters",
      "source":"MODIS",
      "timescale":"January 2006 to present",
      "units":"Alerts",
      "updates":"16 day"
   },
   "params":{  
      "version":"v1",
      "wdpaid":"8950"
   },
   "value":78
}
```

## Concessions

Returns alerts which are linked to a chosen concession. Currently available concessions (:concession) are: mining, oilpalm, fiber, and logging.

```GET http://api.globalforestwatch.org/forest-change/:dataset/use/:concession```

**PARAMETERS**

Parameter | Required | Description
--------- | -------- | -----------
period | false | Period of interest, as comma separated begin and end dates, inclusive. Dates are in YYYY-MM-DD format. Examples: `period=2006-10-08,2008-10-01` for an alert count between 2006-10-08 and 2008-10-01 inclusive, or `period=2008-10-01,2008-10-01` for an alert count for 2008-10-01
download | false | Filename: filename.{csv \| kml \| shp \| geojson \| svg}. If provided the response will be downloaded to a file rather than displayed as html. File type is determined by the filename extension.
dev | false | If exists in query string the returned JSON will include the SQL query
bust | false | If exists in query string the results will be processed even if they have previously been cached 

**EXAMPLE**

http://api.globalforestwatch.org/forest-change/forma-alerts/use/oilpalm/4

**RESPONSE**

```json
{  
   "apis":{  
      "national":"http://api.globalforestwatch.org/forma-alerts/admin{/iso}{?period,download,bust,dev}",
      "subnational":"http://api.globalforestwatch.org/forma-alerts/admin{/iso}{/id1}{?period,download,bust,dev}",
      "use":"http://api.globalforestwatch.org/forma-alerts/use/{/name}{/id}{?period,download,bust,dev}",
      "wdpa":"http://api.globalforestwatch.org/forma-alerts/wdpa/{/id}{?period,download,bust,dev}",
      "world":"http://api.globalforestwatch.org/forma-alerts{?period,geojson,download,bust,dev}"
   },
   "download_urls":{  
      "csv":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+gfw_oil_palm+u%2C+forma_api+f+WHERE+u.cartodb_id+%3D+4+AND+ST_Intersects%28f.the_geom%2C+u.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=csv",
      "geojson":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+gfw_oil_palm+u%2C+forma_api+f+WHERE+u.cartodb_id+%3D+4+AND+ST_Intersects%28f.the_geom%2C+u.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=geojson",
      "kml":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+gfw_oil_palm+u%2C+forma_api+f+WHERE+u.cartodb_id+%3D+4+AND+ST_Intersects%28f.the_geom%2C+u.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=kml",
      "shp":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+gfw_oil_palm+u%2C+forma_api+f+WHERE+u.cartodb_id+%3D+4+AND+ST_Intersects%28f.the_geom%2C+u.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=shp",
      "svg":"http://wri-01.cartodb.com/api/v1/sql?q=SELECT+f.%2A+FROM+gfw_oil_palm+u%2C+forma_api+f+WHERE+u.cartodb_id+%3D+4+AND+ST_Intersects%28f.the_geom%2C+u.the_geom%29+AND+f.date+%3E%3D+%272014-01-01%27%3A%3Adate+AND+f.date+%3C%3D+%272015-01-01%27%3A%3Adate&version=v1&format=svg"
   },
   "max_date":null,
   "meta":{  
      "coverage":"Humid tropical forest biome",
      "description":"Forest disturbances alerts.",
      "id":"forma-alerts",
      "name":"FORMA Alerts",
      "resolution":"500 x 500 meters",
      "source":"MODIS",
      "timescale":"January 2006 to present",
      "units":"Alerts",
      "updates":"16 day"
   },
   "min_date":null,
   "params":{  
      "use":"oilpalm",
      "useid":"4",
      "version":"v1"
   },
   "value":7
}
```
