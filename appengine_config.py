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

sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/python-gflags'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/mandrill'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/docopt'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/requests/requests'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/engineauth'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'gfw'))

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
        return {"error": ("Missing Config File[%s]" % name)}


def _update_config(config, env_path):
    env_config = _load_env_config(env_path)
    if not env_config.get('error'):
        config.update(env_config)

http_host = os.environ.get('HTTP_HOST')

def _get_runtime_config(app_version, env_json, env_yml):
    config = _load_config(env_json)
    _update_config(config, env_yml)
    config['APP_VERSION'] = app_version
    config['APP_BASE_URL'] = 'http://%s' % http_host
    return config


if not http_host:
    appversion, secret, public = ('unittest', 'dev.json', 'local.yml')
elif 'localhost' in http_host:
    appversion, secret, public = ('local', 'dev.json', 'local.yml')
elif 'staging' in http_host:
    appversion, secret, public = ('stage', 'dev.json', 'stage.yml')
else:
    appversion, secret, public = ('production', 'prod.json', 'prod.yml')

runtime_config = _get_runtime_config(appversion, secret, public)

engineauth = {
    # The user will be returned here if an error occurs (default /login):
    'login_uri': '/',
    'redirect_back': True,
    'secret_key': 'SHHHHHH',
    'user_model': 'gfw.user.gfw_user.GFWUser',
}

authentication_keys = runtime_config.get("authentication_keys") or {}
engineauth['provider.twitter'] = authentication_keys.get('twitter')
engineauth['provider.facebook'] = authentication_keys.get('facebook')
engineauth['provider.google'] = authentication_keys.get('google')

def webapp_add_wsgi_middleware(app):
    """Adds authentication middleware."""
    from engineauth import middleware
    return middleware.AuthMiddleware(app)
