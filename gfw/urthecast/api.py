# Internal gfw wrapper for Urthecast's API for tiles

import json
import random

from urllib2 import Request, urlopen, URLError, HTTPError
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
		req = Request(authorized_url)
		try:
			response = urlopen(req)
		except HTTPError as e:
			if hasattr(e, 'reason'):
				self.error_message = {'Reason':e.reason,'Badness':'We failed to reach a server.'}
			elif hasattr(e, 'code'):
				self.error_message = {'Code':e.code,'Badness':'The server could not fulfill the request.'}
			return self.error_message
		else:
			self.data = response.read()
			return self.data
