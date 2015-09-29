from test import common

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