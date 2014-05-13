# API Overview

The Global Forest Watch API is currently in beta. Based on feedback from trusted testers, this document specifies new API changes that are currently under development. Interested in being a trusted tester? Contact the Data Lab (datalab@wri.org) at World Resources Institute. 

# Forest Change API

Forest change measures tree cover loss, tree cover gain, or forest disturbance. The following forest change data are available through the API: University of Maryland tree cover loss & gain, FORMA alerts, IMAZON SAD alerts, QUICC alerts, and NASA active fires.

## FORMA Alerts

FORMA alerts detect areas where tree cover loss is likely to have occurred within the humid tropical biome. The resolution is 500 x 500 meters. Alerts are available for every 16 day period since Janurary 2006. New alerts are continually added every 16 days.

The API supports calculating aggregate alert counts by country, state/province, protected area, use (mining, logging, oil palm, wood fiber plantation areas), and by an arbitrary GeoJSON Polygon or MultiPolygon. You can also specify a time period of interest. Actual alerts (not just aggregated counts) can be downloaded in Shapefile, GeoJSON, CSV, KML, and SVG formats.

---

### Get alert counts

**Parameters**

| **Name** | **Type** | **Description** | **Location** |
|------|------|-------------|--------------|
| iso | string | [3-character ISO country code](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) | Request path |
| id1 | string | [GADM](http://www.gadm.org) id for state/province within a supplied iso code | Request path |
| period | string | Period of interest, as comma separated begin and end dates, inclusive. Dates are in YYYY-MM-DD format. Examples: `period=2006-10-08,2008-10-01` for an alert count between 2006-10-08 and 2008-10-01 inclusive, or `period=,2008-10-01` for an alert count through 2008-10-01 inclusive, or `period=2006-10-01,` for an alert count after 2006-10-01 inclusive  | GET parameter |
| geojson | string | GeoJSON encoded Polygon or MultiPolygon for calculating alerts within their area. Note that this parameter is ignored if your request includes the `iso` and/or `id1` parameters in the request path | GET parameter |
| use | string | Alert count within a specific use area in the form {mining &#124; logging &#124; oilpalm &#124; fiber,polygonid}. Examples: `use=logging,1` for all alerts within logging polygon 1, `use=oilpalm,65` for all alerts within oil palm polygon 65 | GET parameter |
| download | string | Specification for downloading results. Supported formats: csv, geojson, shp, svg, kml. Examples: `download=shp,mydownload` for a Shapefile named mydownload.shp, `download=geojson` for a GeoJSON file with default filename | GET parameter |


**Examples**

Alert count for the entire humid tropical biome:
```
GET /forest-change/forma-alerts
```

[http://beta.gfw-apis.appspot.com/forest-change/forma-alerts](http://beta.gfw-apis.appspot.com/forest-change/forma-alerts)

```json
{
   "coverage":"Humid tropical forest biome",
   "description":"Alerts where forest disturbances have likely occurred.",
   "name": "FORMA",
   "resolution":"500 x 500 meters",
   "source":"MODIS",
   "timescale":"January 2006 to present",
   "units":"Alerts",
   "updates":"16 day",
   "value":2439651
}
```

---

Alert count for the entire humid tropical biome within a specific time period:

```
GET /forest-change/forma-alerts?period={begin,end}|{begin,}|{,end}
```

[http://beta.gfw-apis.appspot.com/forest-change/forma-alerts?period=2010-01-01,2013-01-01](http://beta.gfw-apis.appspot.com/forest-change/forma-alerts?period=2010-01-01,2013-01-01)

```json
{
   "begin":"2010-01-01",
   "coverage":"Humid tropical forest biome",
   "description":"Alerts where forest disturbances have likely occurred.",
   "end":"2013-01-01",
   "name":"FORMA",
   "resolution":"500 x 500 meters",
   "source":"MODIS",
   "timescale":"January 2006 to present",
   "units":"Alerts",
   "updates":"16 day",
   "value":778130
}
```

---

Alert count for the entire humid tropical biome within a GeoJSON polygon:


```
GET /forest-change/forma-alerts?geojson={GeoJSON Polygon or MultiPolygon}
```

[Click here for an example request](http://beta.gfw-apis.appspot.com/forest-change/forma-alerts?geojson=%7B%22coordinates%22%3A%5B%5B%5B98.7890625%2C2.8991526985043006%5D%2C%5B102.83203125%2C-5.703447982149503%5D%2C%5B107.57812499999999%2C-2.7235830833483856%5D%2C%5B98.7890625%2C2.8991526985043006%5D%5D%5D%2C%22type%22%3A%22Polygon%22%7D)

```json
{
   "coverage":"Humid tropical forest biome",
   "description":"Alerts where forest disturbances have likely occurred.",
   "geojson":{
      "coordinates":[
         [
            [
               98.7890625,
               2.8991526985043006
            ],
            [
               102.83203125,
               -5.703447982149503
            ],
            [
               107.57812499999999,
               -2.7235830833483856
            ],
            [
               98.7890625,
               2.8991526985043006
            ]
         ]
      ],
      "type":"Polygon"
   },
   "name":"FORMA",
   "resolution":"500 x 500 meters",
   "source":"MODIS",
   "timescale":"January 2006 to present",
   "units":"Alerts",
   "updates":"16 day",
   "value":189190
}
```

---

Alert count within a specific use area:

```
GET /forest-change/forma-alerts?use={name,pid}
```
http://beta.gfw-apis.appspot.com/forest-change/forma-alerts?use=logging,1

```json
{
   "coverage":"Humid tropical forest biome",
   "description":"Alerts where forest disturbances have likely occurred.",
   "name":"FORMA",
   "resolution":"500 x 500 meters",
   "source":"MODIS",
   "timescale":"January 2006 to present",
   "units":"Alerts",
   "updates":"16 day",
   "use":"logging",
   "use_pid":"1",
   "value":21
}
```

---

Alert count for a country:
```
GET /forest-change/forma-alerts/:iso
```

[http://beta.gfw-apis.appspot.com/forest-change/forma-alerts/bra](http://beta.gfw-apis.appspot.com/forest-change/forma-alerts/bra)

```json
{
   "coverage":"Humid tropical forest biome",
   "description":"Alerts where forest disturbances have likely occurred.",
   "iso":"bra",
   "name": "FORMA",
   "resolution":"500 x 500 meters",
   "source":"MODIS",
   "timescale":"January 2006 to present",
   "units":"Alerts",
   "updates":"16 day",
   "value":1077095
}
```

---

Download alerts for a country:
```
GET /forest-change/forma-alerts/:iso?download={format,filename}
```

[http://beta.gfw-apis.appspot.com/forest-change/forma-alerts/bra?download=csv,brazil_forma](http://beta.gfw-apis.appspot.com/forest-change/forma-alerts/bra?download=csv,brazil_forma)

---

Alert count for a state/province by GADM id:

```
GET /forest-change/forma-alerts/:iso/:id1
```

[http://beta.gfw-apis.appspot.com/forest-change/forma-alerts/bra/10504](http://beta.gfw-apis.appspot.com/forest-change/forma-alerts/bra/10504)


```json
{
   "coverage":"Humid tropical forest biome",
   "description":"Alerts where forest disturbances have likely occurred.",
   "id1":"10504",
   "iso":"bra",
   "name":"FORMA",
   "resolution":"500 x 500 meters",
   "source":"MODIS",
   "timescale":"January 2006 to present",
   "units":"Alerts",
   "updates":"16 day",
   "value":1978
}
```

*Alert count for protected areas and concessions is still under development.*