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

from gfw.lib.topic_result_parsers import TopicResultParsers
from gfw.models.topic_result import TopicResult
from gfw.forestchange import api
from gfw.forestchange import terrai, imazon, prodes, quicc, umd, guyra, glad, viirs

TOPICS = [
    {
        'id': 'alerts/glad',
        'description': 'weekly GLAD tree cover loss alerts',
        'name': 'GLAD Tree Cover Loss Alerts',
        'meta_id': 'glad-alerts',
        'analysis_class': glad,
        'template': '{} alerts',
        'baselayer': 'umd_as_it_happens',
        'parser': TopicResultParsers.simple
    }, {
        'id': 'alerts/terra',
        'description': 'monthly Terra-i tree cover loss alerts',
        'name': 'Terra-i',
        'meta_id': 'terrai-alerts',
        'analysis_class': terrai,
        'template': '{} alerts',
        'baselayer': 'terrailoss',
        'parser': TopicResultParsers.simple
    }, {
        'id': 'alerts/sad',
        'description': 'monthly SAD tree cover loss alerts',
        'name': 'SAD',
        'meta_id': 'imazon-alerts',
        'analysis_class': imazon,
        'template': 'Degradation: {} ha, Deforestation: {} ha',
        'baselayer': 'imazon',
        'parser': TopicResultParsers.sad
    }, {
        'id': 'alerts/quicc',
        'description': 'quarterly QUICC tree cover loss alerts',
        'name': 'QUICC',
        'meta_id': 'quicc-alerts',
        'analysis_class': quicc,
        'template': '{} alerts',
        'baselayer': 'modis',
        'parser': TopicResultParsers.simple
    }, {
        'id': 'alerts/treeloss',
        'description': 'annual tree cover loss data',
        'name': 'Tree cover loss',
        'meta_id': 'umd-loss-gain',
        'analysis_class': umd,
        'template': 'Gain: {} ha, Loss: {} ha',
        'baselayer': 'loss',
        'parser': TopicResultParsers.umd
    }, {
        'id': 'alerts/treegain',
        'description': '12-year tree cover gain data',
        'name': 'Tree cover gain',
        'meta_id': 'umd-loss-gain',
        'analysis_class': umd,
        'template': 'Gain: {} ha, Loss: {} ha',
        'baselayer': 'forestgain',
        'parser': TopicResultParsers.umd
    }, {
        'id': 'alerts/prodes',
        'description': 'annual PRODES deforestation data',
        'name': 'PRODES deforestation',
        'meta_id': 'prodes-loss',
        'analysis_class': prodes,
        'template': '{} ha',
        'baselayer': 'prodes',
        'parser': TopicResultParsers.simple
    }, {
        'id': 'alerts/guyra',
        'description': 'monthly Gran Chaco deforestation data',
        'name': 'Gran Chaco deforestation',
        'meta_id': 'guyra-loss',
        'analysis_class': guyra,
        'template': '{} ha',
        'baselayer': 'guyra',
        'parser': TopicResultParsers.simple
    }, {
        'id': 'alerts/viirs',
        'description': 'daily VIIRS active fires alerts',
        'name': 'VIIRS Active fires',
        'meta_id': 'viirs-active-fires',
        'analysis_class': viirs,
        'template': '{} NASA Active Fires Alerts',
        'baselayer': 'viirs_fires_alerts',
        'parser': TopicResultParsers.viirs
    }
]

class Topic():
    def __init__(self, attributes):
        for key, value in attributes.items():
            setattr(self, key, value)
        self.metadata = api.META[self.meta_id]['meta']

    def execute(self, params):
        params['for_subscription'] = True
        action, data = self.analysis_class.execute(params)
        return TopicResult(self, data)

    @classmethod
    def get_by_id(cls, id):
        topic_attributes = next((t for t in TOPICS if t['id'] == id), None)
        if topic_attributes != None:
            return Topic(topic_attributes)

    @classmethod
    def all(cls):
        return [Topic(t) for t in TOPICS]
