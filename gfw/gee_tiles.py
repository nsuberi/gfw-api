# Global Forest Watch API
# Copyright (C) 2013 World Resource Institute
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

"""This module contains request handlers for serving GEE tiles and was
written by @andrewxhill."""

import os
import ee
import time
import math
import webapp2
import json
import config
import logging

from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.ext import ndb



# definition of auxiliar functions

def _get_key(reqid, request):
  #retrieve reqid
  if reqid == 'landsat_composites':
    return reqid + request.get("year")
  else:
    return reqid

def _get_landsat_tokens(year):
  #retrieve tokens for the landsat images.
  ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
  landSat = ee.Image("LE7_TOA_1YEAR/" + year).select("B3","B2","B1")
  return landSat.getMapId({'opacity': 1, 'gain':3.5, 'bias':4, 'gamma':1.5})

def _get_gcoverage_token():
  # The Green Forest Coverage background created by Andrew Hill
  # example here: http://ee-api.appspot.com/#331746de9233cf1ee6a4afd043b1dd8f
  ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
  treeHeight = ee.Image("Simard_Pinto_3DGlobalVeg_JGR")
  elev = ee.Image('srtm90_v4')
  mask2 = elev.gt(0).add(treeHeight.mask())
  water = ee.Image("MOD44W/MOD44W_005_2000_02_24").select(["water_mask"]).eq(0)
  return treeHeight.mask(mask2).mask(water).getMapId({'opacity': 1, 'min':0, 'max':50, 'palette':"dddddd,1b9567,333333"})

def _get_bwcoverage_token():
  # The Green Forest Coverage background created by Andrew Hill
  # example here: http://ee-api.appspot.com/#331746de9233cf1ee6a4afd043b1dd8f
  ee.Initialize(config.EE_CREDENTIALS, config.EE_URL)
  treeHeight = ee.Image("Simard_Pinto_3DGlobalVeg_JGR")
  elev = ee.Image('srtm90_v4')
  mask2 = elev.gt(0).add(treeHeight.mask())
  return treeHeight.mask(mask2).getMapId({'opacity': 1, 'min':0, 'max':50, 'palette':"ffffff,777777,000000"})


def _retrieve_credentials(max_retries, reqid, meta):
  #Retrieve the mapid and the token for the tiles
  retry_count = 0
  n = 1
  auth = False
  while retry_count < max_retries:
    try:
      auth = True
      return meta[reqid]
      break
    except:
      logging.info('RETRY AUTHENTICATION')
      retry_count += 1
      time.sleep(math.pow(2, n - 1))
      n += 1
      if auth:
        return meta[reqid]
        break

  if not auth or (retry_count == max_retries):
    return





#classes
class TileEntry(ndb.Model):
    value = ndb.BlobProperty()


class MapInit():
    def __init__(self, reqid, request):
      #configure a meta object with the methods we have
      meta = {
      'landsat_composites': _get_landsat_tokens(request.get("year")),
      'simple_green_coverage': _get_gcoverage_token(),
      'simple_bw_coverage': _get_bwcoverage_token()
      }
      key = _get_key(reqid, request)
        
      self.mapid = memcache.get(key)

      if self.mapid is None and reqid in meta:
        self.mapid = _retrieve_credentials(5, reqid, meta)
        # update cache and datastore
        memcache.set(key, self.mapid, time=82800)  # 23 hours
        if self.mapid is None:
          pass
      else:
        pass

# Depricated method, GFW will move to KeysGFW and not deliver tiles from the proxy directly
class TilesGFW(webapp2.RequestHandler):

    def get(self, m, z, x, y):
      year = self.request.get('year', '')
      key = "%s-tile-%s-%s-%s-%s" % (m, z, x, y, year)
      
      cached_image = memcache.get(key)

      if cached_image is None:
        # logging.info('MEMCACHE MISS %s' % key)
        entry = TileEntry.get_by_id(key)
        if entry:
          # logging.info('DATASTORE HIT %s' % key)
          cached_image = entry.value
          memcache.set(key, cached_image)
        else:
          # logging.info('DATASTORE MISS %s' % key)
          pass
      else:
        # logging.info('MEMCAHCE HIT %s' % key)
        pass


      if cached_image is None:
        mapid = MapInit(m.lower(), self.request).mapid
        if mapid is None:
          # TODO add better error code control
          self.error(503)
          logging.warning('mapid is not found')
          return
        else:
          retry_count = 0
          max_retries = 5
          n = 1
          url="https://earthengine.googleapis.com/map/%s/%s/%s/%s?token=%s" % (mapid['mapid'], z, x, y, mapid['token'])

          while retry_count < max_retries:
            try:
              result = urlfetch.fetch(url, deadline=60)
              break
            except:
              logging.info('TILE RETRY %s' % url)
              retry_count += 1
              time.sleep(math.pow(2, n - 1))
              n += 1
        if not result or retry_count == max_retries:
          self.error(503)
          logging.info('result not found')
          return

        if result.status_code == 200:
          memcache.set(key,result.content)
          TileEntry(id=key, value=result.content).put()
          self.response.headers["Content-Type"] = "image/png"
          self.response.headers.add_header("Expires", "Thu, 01 Dec 1994 16:00:00 GMT")
          self.response.out.write(result.content)
        elif result.status_code == 404:
          self.error(404)
          return
        else:
          self.response.set_status(result.status_code)
      else:
        # logging.info('CACHE HIT %s' % key)
        self.response.headers["Content-Type"] = "image/png"
        self.response.headers.add_header("Expires", "Thu, 01 Dec 1994 16:00:00 GMT")
        self.response.out.write(cached_image)


class KeysGFW(webapp2.RequestHandler):
    def get(self, m, year=None):

      mapid = MapInit(m.lower(), self.request).mapid

      if mapid is None:
        # TODO add better error code control
        self.error(404)
      else:
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({
            'mapid' : mapid['mapid'],
            'token' : mapid['token']
          }))


api = webapp2.WSGIApplication([ 
    ('/gee/([^/]+)/([^/]+)/([^/]+)/([^/]+).png', TilesGFW), 
    ('/gee/([^/]+)', KeysGFW)

  ], debug=True)


