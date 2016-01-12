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
This module monkey patches (sorry!) EngineAuth's OAuth implementations
so that they redirect to the GFW profile page if the user doesn't have
an email address on their profile.
"""

def setup():
    def callback(self, req):
        import cPickle as pickle
        flow = pickle.loads(req.session.data.get(self.session_key))
        if flow is None:
            self.raise_error('And Error has occurred. Please try again.')
        req.credentials = flow.step2_exchange(req.params)
        user_info = self.user_info(req)
        profile = self.get_or_create_profile(
            auth_id=user_info['auth_id'],
            user_info=user_info,
            credentials=req.credentials)
        req.load_user_by_profile(profile)

        if not hasattr(profile, 'email') or not profile.email:
            from urlparse import urlparse
            redirect_uri = req.get_redirect_uri()
            parsed_uri = urlparse(redirect_uri)
            return '{uri.scheme}://{uri.netloc}/my_gfw/?redirect={redirect}'.format(
                uri=parsed_uri, redirect=redirect_uri)
        else:
            return req.get_redirect_uri()

    from engineauth.strategies import oauth
    from engineauth.strategies import oauth2

    oauth.OAuthStrategy.callback = callback
    oauth2.OAuth2Strategy.callback = callback
