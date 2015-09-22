# gfw proxy to hit internally wrapped urthecast api
# Methods to search ndb for memcached tiles or to create and remove ndb records of memcached tiles.

# https://tile-{s}.urthecast.com/v1

import webapp2
import json

from google.appengine.api import memcache

from gfw.urthecast.api import Urthecast

uc = Urthecast()

class UrthecastHandler(webapp2.RequestHandler):

	def _build_tiles_key(self,uri_string):
		uri = {}
		items = uri_string.split('/')
		uri['renderer']=items[1]
		uri['z']=items[2]
		uri['x']=items[3]
		uri['y']=items[4]
		tiles_key = "%s-tile-%s-%s-%s" % (uri['renderer'],uri['z'],uri['x'],uri['y'])
		return tiles_key

	def get_data(self,urthecast_url_part):
		tiles_key = self._build_tiles_key(urthecast_url_part)
		data = memcache.get(tiles_key)
		if data is not None:
			# print "FOUND within cache with key value: " + tiles_key
			return data
		else:
			uc.tiles(urthecast_url_part)
			data = uc.data
			if data:
				memcache.add(tiles_key, data, 60)
				# if memcache.add(tiles_key, data, 60):
				# 	print 'CREATED within memcache'
				# else:
				# 	print 'COULD NOT create in memcache'
		return data

	def tiles(self, *args, **kwargs):
		urthecast_url_part = self.request.path_qs.replace('urthecast/map-tiles/','')
		data = self.get_data(urthecast_url_part)
		self._set_response('image/png',data)

	def _set_response(self,content_type,data):
		if not data:
			content_type = 'application/json'
			response = json.dumps(uc.error_message)
		else:
			response = data
		self.response.headers.add('Content-Type', content_type)
		self.response.write(response)

routes = [
		webapp2.Route(
			r'/urthecast/map-tiles/<:.*>', 
			handler=UrthecastHandler,
			handler_method='tiles',
			methods=['GET']
		)
	]

	
app = webapp2.WSGIApplication(routes, debug=True)

