from test import common
from appengine_config import runtime_config

import unittest
import webapp2
import webtest

import gfw.urthecast.api as urthecast

import json
import requests
import mock

class RequestsFaker():
	def __init__(self,json,status_code=None):
		self.fake_json = json
		self.status_code = status_code

	def json(self):
		return self.fake_json

class UrthecastTest(unittest.TestCase):

	def setUp(self):
		self.uc = urthecast.Urthecast()

		self.error_dict = {'payload':None,'error':'Error Message'}
		self.error_response = RequestsFaker(self.error_dict)

		self.fake_payload = "Valid but faked Payload"
		valid_dict = {'payload':[self.fake_payload]}
		self.valid_response = RequestsFaker(valid_dict)
		self.params_dict = {'api_key': self.uc.key, 'api_secret': self.uc.secret}
		self.fake_id = 'fake_id'
		self.valid_tiles_response = 'Valid tiles response mockery'
		self.fake_url_part = '/fake/as/hell'

	def test___init__(self):
		self.uc = urthecast.Urthecast('fake_key','fake_secret')
		self.assertEqual(self.uc.key,'fake_key')
		self.assertEqual(self.uc.secret,'fake_secret')
		self.uc = urthecast.Urthecast()
		self.assertIsNone(self.uc.data)
		self.assertIsNone(self.uc.error_message)
		self.assertEqual(self.uc.key,runtime_config.get("urthecast_key"))
		self.assertEqual(self.uc.secret,runtime_config.get("urthecast_secret"))

	@mock.patch('urllib2.Request')
	def test_tiles(self, mock_Request_tiles):
		mock_Request_tiles.return_value = self.valid_tiles_response
		r = self.uc.tiles(self.fake_url_part)




	@mock.patch('urllib2.Request')
	def test_scenes(self, mock_Request_scenes):
		self.assertEqual(2,3)



if __name__ == '__main__':
	unittest.main(exit=False, failfast=True)
