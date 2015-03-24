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
import yaml


def fix_path():
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'gfw'))

fix_path()

#
#  LOADERS: 
#

def _load_config(name):
    """Return dev config environment as dictionary."""
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), name)
    try:
        return json.loads(open(path, "r").read())
    except:
        return {}

def _load_env_config(name):
    """Return dev config environment as dictionary."""
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), name)
    try:
        cfig = yaml.load(open(path, "r").read())
        return cfig
    except:
        return {"error": ("Missing Config File[%s]" % name) }

#
#  CONFIG HELPERS: 
#

def _update_config(config,env_path):
    env_config = _load_env_config(env_path)
    if not env_config.get('error'):
        config.update(env_config)

http_host = os.environ.get('HTTP_HOST')

def _get_runtime_config(env_type,env_json,env_yml):
    config = _load_config(env_json)
    _update_config(config,env_yml)
    config['ENV_TYPE'] = env_type
    config['APP_BASE_URL'] = 'http://%s' % http_host
    return config

#
# SET ENV
#
if not http_host:
    envtype, secret, public = ('unit-test', 'dev.json', 'local.yml')
elif 'localhost' in http_host:
    envtype, secret, public = ('local', 'dev.json', 'local.yml')
elif 'dev' in http_host:
    envtype, secret, public = ('dev', 'dev.json', 'dev.yml')
elif 'stage' in http_host:
    envtype, secret, public = ('stage', 'dev.json', 'stage.yml')
else:
    envtype, secret, public = ('prod', 'prod.json', 'prod.yml')

#
# RUNTIME CONFIG
#
runtime_config = _get_runtime_config(envtype, secret, public)
