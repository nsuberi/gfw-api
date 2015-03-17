# Global Forest Watch API
# Copyright (C) 2013 World Resource Institute
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

"""This module provides App Engine configurations."""

import json
import os
import sys


def fix_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'gfw'))

fix_path()


def _load_config(name):
    """Return dev config environment as dictionary."""
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), name)
    try:
        return json.loads(open(path, "r").read())
    except:
        return {}


#
#  ENV Setup: 
#
def test_config():
    config = _load_config('dev.json')
    config['IS_DEV'] = True
    config['APP_BASE_URL'] = 'http://localhost:8080'
    return config

def dev_config():
    config = _load_config('dev.json')
    config['IS_DEV'] = True
    config['APP_BASE_URL'] = 'http://%s' % http_host
    return config

def prod_config():
    config = _load_config('prod.json')
    config['IS_DEV'] = False
    config['APP_BASE_URL'] = 'http://gfw-apis.appspot.com'
    return config

http_host = os.environ.get('HTTP_HOST')

if not http_host:
    runtime_config = test_config()
elif 'localhost' in http_host:
    runtime_config = dev_config()
elif 'dev' in http_host:
    runtime_config = dev_config()
elif 'stage' in http_host:
    runtime_config = dev_config()
else:
    runtime_config = prod_config()
