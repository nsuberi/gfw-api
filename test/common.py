# Global Forest Watch API
# Copyright (C) 2014 World Resource Institute
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Common test classes"""


import itertools
import unittest

from google.appengine.ext import testbed

from google.appengine.api import apiproxy_stub
from google.appengine.api import apiproxy_stub_map
from google.appengine.ext import ndb

import appengine_config

CDB_URL = 'https://wri-01.cartodb.com/api/v2/sql?%s'


def combos(params, repeat=None, min=None):
    """Returns a sequence of param tuples (name, value)."""
    result = set()
    if not repeat:
        repeat = len(params) + 1
    if not min:
        min = 1
    for x in range(min, repeat):
        result.update(itertools.combinations(params, x))
    result = list(result)
    result.append(())
    return result


class BaseTest(unittest.TestCase):

    """Base class for unit tests."""

    def setUp(self):
        """Setup testbed and testapp rig."""
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_urlfetch_stub()
        self.testbed.init_app_identity_stub()
        self.testbed.init_blobstore_stub()
        self.testbed.init_taskqueue_stub(root_path='.')
        self.taskqueue_stub = self.testbed.get_stub(
            testbed.TASKQUEUE_SERVICE_NAME)
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)
        ndb.get_context().clear_cache()

    def tearDown(self):
        self.testbed.deactivate()


class FetchBaseTest(unittest.TestCase):

    """Base class for mocked urlfetch"""

    def setUp(self):
        unittest.TestCase.setUp(self)
        apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
        self._mock = URLFetchServiceMock()
        apiproxy_stub_map.apiproxy.RegisterStub("urlfetch", self._mock)

        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.testbed.init_app_identity_stub()
        self.testbed.init_blobstore_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def setResponse(self, **kwargs):
        """Set the return value."""
        self._mock.set_return_values(kwargs)

    def tearDown(self):
        unittest.TestCase.tearDown(self)


class URLFetchServiceMock(apiproxy_stub.APIProxyStub):

    """Mock for google.appengine.api.urlfetch."""

    def __init__(self, service_name='urlfetch'):
        super(URLFetchServiceMock, self).__init__(service_name)

    def set_return_values(self, kwargs):
        self.return_values = kwargs

    def _Dynamic_Fetch(self, request, response):
        return_values = self.return_values
        response.set_content(return_values.get('content', ''))
        response.set_statuscode(return_values.get('status_code', 200))

        for header_key, header_value \
                in return_values.get('headers', {}).items():
            new_header = response.add_header()
            new_header.set_key(header_key)
            new_header.set_value(header_value)
        response.set_finalurl(return_values.get('final_url', request.url()))
        response.set_contentwastruncated(return_values.get(
            'content_was_truncated', False))

        self.request = request
        self.response = response
