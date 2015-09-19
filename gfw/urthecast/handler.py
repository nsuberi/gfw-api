# gfw proxy to hit internally wrapped urthecast api
# Methods to search ndb for memcached tiles or to create and remove ndb records of memcached tiles.

import webapp2
import json

from gfw.urthecast.api import Urthecast
from gfw.urthecast.model import TilesUC

uc = Urthecast()

class UrthecastHandler(webapp2.RequestHandler):
	
	def _get_uri_params(uri_string):
		# returns uri parameters as a dictionary - only set to work on simple tiles...
		# TODO extend to work with any uri for urthecast tiles
		params = {}
		items = uri_string.split('/')
		params['renderer']=items[0]
		params['z']=items[1]
		params['x']=items[2]
		params['y']=items[3]
		return params


    def tiles(self,*args, **kwargs):
        # a-h = {s} - just a server choice
        # https://tile-{s}.urthecast.com/v1
        urthecast_url_part = self.request.path_qs.replace('urthecast/map-tiles/','')
        p = _get_uri_params(urthecast_url_part)

        key = "%s-tile-%s-%s-%s" % (p['renderer'],p['z'],p['x'],p['y'])

        uct = TilesUC.search_for(cls,key)




        uc.tiles(urthecast_url_part)
        self._set_response('image/png')

    def archive(self, *args, **kwargs):
        # https://api.urthecast.com/v1/archive/scenes
        urthecast_url_part = self.request.path_qs.replace('urthecast/archive/','')
        uc.scenes(urthecast_url_part)
        self._set_response('application/json')
    
    def _set_response(self,content_type):
        if uc.error_message:
            content_type = 'application/json'
            response = json.dumps(uc.error_message)
        else:
            response = uc.data
        self.response.headers.add('Content-Type', content_type)
        self.response.write(response)

routes = [
        webapp2.Route(
            r'/urthecast/map-tiles/<:.*>', 
            handler=UrthecastHandler,
            handler_method='tiles',
            methods=['GET']
        ),

        webapp2.Route(
            r'/urthecast/archive/<:.*>', 
            handler=UrthecastHandler,
            handler_method='archive',
            methods=['GET']
        )
        
    ]

    
app = webapp2.WSGIApplication(routes, debug=True)

