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
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/engineauth'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/engineauth'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'lib/engineauth'))
    sys.path.append(os.path.join(os.path.dirname(__file__), 'gfw'))

fix_path()


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
elif 'dev' in http_host:
    appversion, secret, public = ('dev', 'dev.json', 'dev.yml')
elif 'stage' in http_host:
    appversion, secret, public = ('stage', 'dev.json', 'stage.yml')
else:
    appversion, secret, public = ('production', 'prod.json', 'prod.yml')


runtime_config = _get_runtime_config(appversion, secret, public)

engineauth = {
    # The user will be returned here if an error occurs (default /login):
    'login_uri': '/',
    # The user is sent here after successfull authentication:
    'redirect_back': True,
    'secret_key': 'SHHHHHH',
    # Comment out to use default User and UserProfile models:
    # 'user_model': 'models.CustomUser',
}

# Twitter Authentication
engineauth['provider.twitter'] = {
    'client_id': 'jgQR7Lg8gLkl9CqziHUoJE4d6',
    'client_secret': '1pWqfBlPsUyC8Od6kaG0tXcVWaFWaVac7IhU8EhKP0P1U0g73F',
}

# Facebook Authentication
# Currently on dev credentials using Dave P's Account
engineauth['provider.facebook'] = {
    'client_id': '1011581985558615',
    'client_secret': 'd8b03e57d2bbbf56c8bc98bbe9d32ee4',
    'scope': 'email',
}

# Google Plus Authentication
# Currently using Dave P's Account
engineauth['provider.google'] = {
    'client_id': '324237003660-j10fbal3v9hie743mvl16mcu'
    '4hvvi7pl.apps.googleusercontent.com',
    'client_secret': 'QGvyzZajrfqkg3DIVMfq6BwL',
    'api_key': 'CHANGE_TO_GOOGLE_API_KEY',
    'scope': 'https://www.googleapis.com/auth/plus.me',
}

# LinkedIn Authentication
# Currently using Dave P's Account
engineauth['provider.linkedin'] = {
    'client_id': '75b0lcdhgxqf64',
    'client_secret': 'M09xlYP6cHKEHSDj',
}

# GitHub Authentication
# Currently using Dave P's Account
engineauth['provider.github'] = {
    'client_id': 'ca82b0d062ce107c031d',
    'client_secret': 'e2d0420f8abd67d5fc4f8bdefd9e8144744bf3e8',
}


def webapp_add_wsgi_middleware(app):
    """Adds authentication middleware."""
    from gfw.middlewares import oauth
    oauth.setup()

    from engineauth import middleware
    return middleware.AuthMiddleware(app)
