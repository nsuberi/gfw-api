# Internal gfw wrapper for Urthecast's API for tiles
import logging
import json
import random
import time

from appengine_config import runtime_config
from google.appengine.api import urlfetch

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
		url = 'https://api.urthecast.com/v1/archive/scenes{url_part}'.format(url_part=url_part)
		return self._request_url(url)

	def _request_url(self,url):
		if '?' in url:
			authorized_tmpl = "{url}&api_key={key}&api_secret={secret}"
		else:
			authorized_tmpl = "{url}?api_key={key}&api_secret={secret}"

		authorized_url = authorized_tmpl.format(url=url,key=self.key,secret=self.secret)
		
		max_retry = 2
		retry_count = 0
		retry = True
		t = 5 # Time to wait between raised HTTPException and calling again

		while retry:
			retry = False
			e = None
			try:
				result = urlfetch.fetch(authorized_url)
				if result.status_code == 200:
					self.data = result.content
				else:
					self.error_message = {'Code':result.status_code}
					logging.error('********* THERE IS NO DATA but NO exception is thrown. status code is !=200 **********')
			except urlfetch.InvalidURLError, e:
				logging.error('********* Invalid url ***********: %s'%str(e))
			except urlfetch.DownloadError:
				retry_count += 1
				if retry_count < max_retry:
					logging.info('Trying again; re-attempt number '+str(retry_count))
					retry = True
					logging.info('Sleeping for '+str(t)+' seconds')
		 			time.sleep(t)
		 		else:
					logging.info('Last retry also timed out.')
		 			e = 'Multiple Timeouts'
				logging.error('********** Download Error ************: %s'% str(e))
			except Exception, e:
				logging.error('********** Generic Exception ************: %s'%str(e))
			if e:
				self.error_message = {'Exception string':str(e)}
		return self.data

