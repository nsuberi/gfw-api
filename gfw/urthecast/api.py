# Internal gfw wrapper for Urthecast's API for tiles
import logging
import json
import random
import time

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

		req = urllib2.Request(authorized_url)
		while retry:
			retry = False		
			try:
				response = urllib2.urlopen(req)
			except ValueError, e:
				logging.error('Threw ValueError; Invalid URL')
				self.error_message = {'Raised ValueError':'Invalid URL?'}
			except urllib2.HTTPError, e:
				logging.error('HTTPError = '+str(e.code))
				self.error_message = {'HTTPError':e.code}
			except urllib2.URLError, e:
				logging.error('URLError. Reason= '+str(e.reason)+', args= '+str(e.args))
				self.error_message = {'URLError':'Exception raised'}
			except httplib.HTTPException, e:
				retry_count += 1
				logging.error('HTTPException'+str(e.args))
				if retry_count < max_retry:
					logging.info('Trying again; re-attempt number '+str(retry_count))
					retry = True
					logging.info('Sleeping for '+str(t)+' seconds')
					time.sleep(t)
				else:
					logging.info('Last retry also timed out.')
					self.error_message = {'reason':'Timeout Error','code':503}
			except Exception:
				import traceback
				logging.error('generic exception: '+traceback.format_exc())
				self.error_message = {'Exception':'500'} # Don't know if this is an informative code
			else:
				logging.info('Status:'+str(response.code))
				self.data = response.read()
				return self.data
