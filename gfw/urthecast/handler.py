# gfw proxy to hit internally wrapped urthecast api
# Methods to search ndb for memcached tiles or to create and remove ndb records of memcached tiles.

# https://tile-{s}.urthecast.com/v1

import webapp2
import json

from google.appengine.api import memcache

from gfw.urthecast.api import Urthecast

uc = Urthecast()

class UrthecastHandler(webapp2.RequestHandler):

        def get_data(self,urthecast_url_part):
                expire = 3600

                uc.tiles(urthecast_url_part)

                return uc.data

                #### testing speed #####

                # data = memcache.get(urthecast_url_part)
                # if data is not None:
                #       return data
                # else:
                #       uc.tiles(urthecast_url_part)
                #       data = uc.data
                #       if data:
                #               memcache.add(urthecast_url_part, data, time=expire)
                # return data

        def tiles(self, *args, **kwargs):
                uc.data = None
                uc.error_message = None
                urthecast_url_part = self.request.path_qs.replace('urthecast/map-tiles/','')
                data = self.get_data(urthecast_url_part)
                self._set_response('image/png',data)

        def archive(self, *args, **kwargs):
                # https://api.urthecast.com/v1/archive/scenes
                urthecast_url_part = self.request.path_qs.replace('urthecast/archive/scenes/','')
                response_dict = json.dumps(json.loads(uc.scenes(urthecast_url_part)))
                self._set_response('application/json',response_dict)

        def _set_response(self,content_type,data):
                if not data:
                        content_type = 'application/json'
                        response = json.dumps(uc.error_message)
                else:
                        response = data

                self.response.headers.add('Content-Type', content_type)
                self.response.headers['Access-Control-Allow-Origin'] = '*'
                self.response.headers['Access-Control-Allow-Headers'] = \
                    'Origin, X-Requested-With, Content-Type, Accept'
                self.response.headers['Access-Control-Allow-Methods'] = 'GET'

                self.response.write(response)

routes = [
                webapp2.Route(
                        r'/urthecast/map-tiles/<:.*>',
                        handler=UrthecastHandler,
                        handler_method='tiles',
                        methods=['GET']
                ),
                webapp2.Route(
                        r'/urthecast/archive/scenes/<:.*>',
                        handler=UrthecastHandler,
                        handler_method='archive',
                        methods=['GET']
                )
        ]


app = webapp2.WSGIApplication(routes, debug=True)

