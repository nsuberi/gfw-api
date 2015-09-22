# gfw proxy to hit internally wrapped urthecast api
# Methods to search ndb for memcached tiles or to create and remove ndb records of memcached tiles.

# https://tile-{s}.urthecast.com/v1

import webapp2
import json

from google.appengine.api import memcache
from gfw.urthecast.api import Urthecast
# from gfw.urthecast.model import TilesUC

uc = Urthecast()

class UrthecastHandler(webapp2.RequestHandler):

	def _get_uri_params(self,uri_string):
		# returns uri parameters as a dictionary - only set to work on simple tiles...
		# TODO extend to work with any uri for urthecast tiles - return uri_dict and params_dict
		uri = {}
		items = uri_string.split('/')
		uri['renderer']=items[1]
		uri['z']=items[2]
		uri['x']=items[3]
		uri['y']=items[4]
		return uri

	def tiles(self, *args, **kwargs):
		self.response.headers['Content-Type'] = 'text/plain'
		self.response.write('Hello, World!')
		urthecast_url_part = self.request.path_qs.replace('urthecast/map-tiles/','')
		print "**********"
		print "**********"
		print "**********"
		print urthecast_url_part
		p = self._get_uri_params(urthecast_url_part)
		print p
		tiles_key = "%s-tile-%s-%s-%s" % (p['renderer'],p['z'],p['x'],p['y'])
		print tiles_key
		print "**********"
		print "**********"
		print "**********"
		# uct = TilesUC.search_for(cls,tiles_key)
		uc.tiles(urthecast_url_part)
		self._set_response('image/png')

	def _set_response(self,content_type):
		if uc.error_message:
			content_type = 'application/json'
			response = json.dumps(uc.error_message)
		else:
			response = uc.data
		self.response.headers.add('Content-Type', content_type)
		self.response.write(response)

	def get_tiles(self, tiles_key):
		# Expecting strings for a string tiles_key
		tiles = memcache.get(tiles_key)

routes = [
		webapp2.Route(
			r'/urthecast/map-tiles/<:.*>', 
			handler=UrthecastHandler,
			handler_method='tiles',
			methods=['GET']
		)
	]

	
app = webapp2.WSGIApplication(routes, debug=True)

