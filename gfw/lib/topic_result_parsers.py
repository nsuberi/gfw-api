# Global Forest Watch API
# Copyright (C) 2015 World Resource Institute
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

class TopicResultParsers:
    @classmethod
    def simple(cls, data):
        return [data.get('value')]

    @classmethod
    def viirs(cls, data):
        if data.get('value') != None:
            return [data.get('value')]
        else:
            return [len(data.get('results')), data.get('results')]

    @classmethod
    def sad(cls, data):
        a = data.get('value')[0]
        b = data.get('value')[1]
        if a.get('data_type') == 'degrad':
            return [a.get('value'), b.get('value')]
        else:
            return [b.get('value'), a.get('value')]

    @classmethod
    def umd(cls, data):
        return [data.get('gain'), data.get('loss')]
