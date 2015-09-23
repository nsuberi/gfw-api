# Internal gfw wrapper for Urthecast's API for tiles
import logging
import json
import random

import httplib
import urllib2
from appengine_config import runtime_config

class Urthecast:

	def __init__(self, key=None, secret=None):
		# Initializes an urthecastAPI caller based on a user's passed secrets
		# or secrets stored in private dev.json and prod.json files
		self.data = None
		self.error_message = None
		self.key = key or runtime_config.get("urthecast_key")
		self.secret = secret or runtime_config.get("urthecast_secret")

	def tiles(self,url_part):
		s = random.choice(['a','b','c','d','e','f','g','h'])
		url = 'https://tile-{s}.urthecast.com/v1/{url_part}'.format(s=s,url_part=url_part)
		return self._request_url(url)

	def scenes(self,url_part):
		url = 'https://api.urthecast.com/v1/archive/scenes'.format(url_part=url_part)
		return self._request_url(url)

	def _request_url(self,url):
		if '?' in url:
			authorized_tmpl = "{url}&api_key={key}&api_secret={secret}"
		else:
			authorized_tmpl = "{url}?api_key={key}&api_secret={secret}"
		authorized_url = authorized_tmpl.format(url=url,key=self.key,secret=self.secret)
		req = urllib2.Request(authorized_url)
		try:
			response = urllib2.urlopen(req)
		except urllib2.HTTPError, e:
			logging.error('HTTPError = hella' + str(e.code))
		except urllib2.URLError, e:
			logging.error('URLError = ' + str(e.reason))
		except httplib.HTTPException, e:
			logging.error('HTTPException')
		except Exception:
			import traceback
			logging.error('generic exception: ' + traceback.format_exc())
		else:
			self.data = response.read()
			return self.data
