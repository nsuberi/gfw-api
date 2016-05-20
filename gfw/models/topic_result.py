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

class TopicResult:
    def __init__(self, topic, data):
        self.topic = topic
        self.data = data

    def is_zero(self):
        if 'results' in self.data:
            return len(self.data.get('results')) == 0
        else:
            return all(float(v or 0) == 0 for v in self.value())

    def value(self):
        return self.topic.parser(self.data)

    def formatted_value(self):
        value = map(str, self.value())
        return self.topic.template.format(*value)

    def area_name(self):
        params = self.data['params']

        if 'id1' in params.keys():
            return "ID1: " + params.get('id1')
        elif 'iso' in params.keys():
            return "ISO Code: " + params.get('iso')
        elif 'wdpaid' in params.keys():
            return "WDPA ID: " + str(params.get('wdpaid'))
        else:
            return "Custom area"
