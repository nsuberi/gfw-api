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

"""
This module monkey patches (sorry!) EngineAuth's middleware so that it
doesn't update its stored redirect URI if it's in the middle of an OAuth
flow (mostly happens when logging in to facebook)
"""

def setup():
    def _set_redirect_back(self):
        if "callback" not in self.url:
            next_uri = self.referer
            if next_uri is not None and self._config['redirect_back']:
                self.session.data['_redirect_uri'] = next_uri

    from engineauth.middleware import EngineAuthRequest
    EngineAuthRequest._set_redirect_back = _set_redirect_back
