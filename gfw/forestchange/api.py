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

"""This module is the entry point for the forest change API."""

import logging
import re
import webapp2

from gfw.forestchange import forma
from gfw.forestchange import fires
from gfw.forestchange import umd
from gfw.forestchange import quicc
from gfw.forestchange import imazon
from gfw.forestchange import args
from gfw.common import CORSRequestHandler
from gfw.common import APP_BASE_URL

FORMA_API = '%s/forma-alerts' % APP_BASE_URL
UMD_API = '%s/umd-loss-gain' % APP_BASE_URL
FIRES_API = '%s/nasa-active-fires' % APP_BASE_URL
QUICC_API = '%s/quicc-alerts' % APP_BASE_URL
IMAZON_API = '%s/imazon-alerts' % APP_BASE_URL

META = {
    'forma-alerts': {
        'meta': {
            "description": "Forest disturbances alerts.",
            "resolution": "500 x 500 meters",
            "coverage": "Humid tropical forest biome",
            "timescale": "January 2006 to present",
            "updates": "16 day",
            "source": "MODIS",
            "units": "Alerts",
            "name": "FORMA",
            "id": "forma-alerts"
        },
        'apis': {
            'world': '%s{?period,geojson,download,bust,dev}' % FORMA_API,
            'national': '%s/admin{/iso}{?period,download,bust,dev}' %
            FORMA_API,
            'subnational': '%s/admin{/iso}{/id1}{?period,download,bust,dev}' %
            FORMA_API,
            'use': '%s/use/{/name}{/id}{?period,download,bust,dev}' %
            FORMA_API,
            'wdpa': '%s/wdpa/{/id}{?period,download,bust,dev}' %
            FORMA_API
        }
    },
    'nasa-active-fires': {
        'meta': {
            "description": "Displays fire alert data for the past 7 days.",
            "resolution": "1 x 1 kilometer",
            "coverage": "Global",
            "timescale": "Last 7 days",
            "updates": "Daily",
            "source": "MODIS",
            "units": "Alerts",
            "name": "NASA Active Fires",
            "id": "nasa-active-fires"
        },
        'apis': {
            'world': '%s{?period,geojson,download,bust,dev}' % FIRES_API,
            'national': '%s/admin{/iso}{?period,download,bust,dev}' %
            FIRES_API,
            'subnational': '%s/admin{/iso}{/id1}{?period,download,bust,dev}' %
            FIRES_API,
            'use': '%s/use/{/name}{/id}{?period,download,bust,dev}' %
            FIRES_API,
            'wdpa': '%s/wdpa/{/id}{?period,download,bust,dev}' %
            FIRES_API
        }
    },
    'quicc-alerts': {
        'meta': {
            "description": "Identifies areas of land that have lost at least \
            40% of their green vegetation cover from the previous quarterly \
            product.",
            "resolution": "5 x 5 kilometer",
            "coverage": "Global, except for areas >37 degrees north",
            "timescale": "October 2011-present",
            "updates": "Quarterly (April, July, October, January)",
            "source": "MODIS",
            "units": "Alerts",
            "name": "QUICC Alerts",
            "id": "quicc-alerts"
        },
        'apis': {
            'global': '%s{?period,geojson,download,bust,dev}' % QUICC_API,
            'national': '%s/admin{/iso}{?period,download,bust,dev}' %
            QUICC_API,
            'subnational': '%s/admin{/iso}{/id1}{?period,download,bust,dev}' %
            QUICC_API,
            'use': '%s/use/{/name}{/id}{?period,download,bust,dev}' %
            QUICC_API,
            'wdpa': '%s/wdpa/{/id}{?period,download,bust,dev}' %
            QUICC_API
        }
    },
    'imazon-alerts': {
        'meta': {
            "description": "Deforestation alert system that monitors forest \
            cover loss and forest degradation.",
            "resolution": "250 x 250 meters",
            "coverage": "Brazilian Amazon",
            "timescale": "January 2007-present",
            "updates": "Monthly",
            "source": "MODIS, validated with Landsat and CBERS",
            "units": "Alerts",
            "name": "IMAZON Alerts",
            "id": "imazon-alerts"
        },
        'apis': {
            'global': '%s{?period,geojson,download,bust,dev}' % IMAZON_API,
            'national': '%s/admin{/iso}{?period,download,bust,dev}' %
            IMAZON_API,
            'subnational': '%s/admin{/iso}{/id1}{?period,download,bust,dev}' %
            IMAZON_API,
            'use': '%s/use/{/name}{/id}{?period,download,bust,dev}' %
            IMAZON_API,
            'wdpa': '%s/wdpa/{/id}{?period,download,bust,dev}' %
            IMAZON_API
        }
    },    'umd-loss-gain': {
        'meta': {
            "description": "Identifies areas of tree cover loss and gain.",
            "resolution": "30 x 30 meters",
            "coverage": "Global land area (excluding Antarctica and other \
                Arctic islands)",
            "timescale": "January 2000-2012",
            "updates": "Loss: Annual, Gain: 12-year cumulative, updated \
                annually",
            "source": "Landsat 7 ETM+",
            "units": "Percents and hectares",
            "name": "University of Maryland tree cover loss and gain",
            "id": "umd-loss-gain"
        },
        'apis': {
            'national': '%s/admin{/iso}{?bust,dev,thresh}' %
            UMD_API,
            'subnational': '%s/admin{/iso}{/id1}{?bust,dev,thresh}' %
            UMD_API,
        }
    }
}

# Maps dataset to accepted query params
PARAMS = {
    'forma-alerts': {
        'all': ['period', 'download', 'geojson', 'dev', 'bust'],
        'iso': ['period', 'download', 'dev', 'bust'],
        'id1': ['period', 'download', 'dev', 'bust'],
        'wdpa': ['period', 'download', 'dev', 'bust'],
        'use': ['period', 'download', 'dev', 'bust'],
    },
    'nasa-active-fires': {
        'all': ['period', 'download', 'geojson', 'dev', 'bust'],
        'iso': ['period', 'download', 'dev', 'bust'],
        'id1': ['period', 'download', 'dev', 'bust'],
        'wdpa': ['period', 'download', 'dev', 'bust'],
        'use': ['period', 'download', 'dev', 'bust'],
    },
    'quicc-alerts': {
        'all': ['period', 'download', 'geojson', 'dev', 'bust'],
        'iso': ['period', 'download', 'dev', 'bust'],
        'id1': ['period', 'download', 'dev', 'bust'],
        'wdpa': ['period', 'download', 'dev', 'bust'],
        'use': ['period', 'download', 'dev', 'bust'],
    },
    'imazon-alerts': {
        'all': ['period', 'download', 'geojson', 'dev', 'bust'],
        'iso': ['period', 'download', 'dev', 'bust'],
        'id1': ['period', 'download', 'dev', 'bust'],
        'wdpa': ['period', 'download', 'dev', 'bust'],
        'use': ['period', 'download', 'dev', 'bust'],
    },
    'umd-loss-gain': {
        'all': ['thresh', 'geojson', 'period', 'dev', 'bust'],
        'iso': ['download', 'dev', 'bust', 'thresh'],  # TODO: thresh
        'id1': ['download', 'dev', 'bust', 'thresh'],  # TODO: thresh
    }
}

# Maps dataset name to target module for execution
TARGETS = {
    'forma-alerts': forma,
    'umd-loss-gain': umd,
    'nasa-active-fires': fires,
    'quicc-alerts': quicc,
    'imazon-alerts': imazon
}


def _dataset_from_path(path):
    """Return dataset name from supplied request path.

    Path format: /forest-change/{dataset}/..."""
    tokens = path.split('/')
    return tokens[2] if len(tokens) >= 1 else None


def _classify_request(path):
    """Classify request based on supplied path.

    Returns 2-tuple (dataset,request_type)

    Example: /forest-change/forma-alerts/admin/iso => (forma-alerts, iso)"""
    dataset = _dataset_from_path(path)
    rtype = None
    hit = None

    hit = re.match(r'/forest-change/%s$' % dataset, path)
    if hit:
        return dataset, 'all'

    hit = re.match(r'/forest-change/%s/admin/[A-z]{3,3}$' % dataset, path)
    if hit:
        return dataset, 'iso'

    hit = re.match(r'/forest-change/%s/admin/[A-z]{3,3}/\d+$' % dataset, path)
    if hit:
        return dataset, 'id1'

    hit = re.match(r'/forest-change/%s/wdpa/\d+$' % dataset, path)
    if hit:
        return dataset, 'wdpa'

    hit = re.match(r'/forest-change/%s/use/[A-z]+/\d+$' % dataset, path)
    if hit:
        rtype = 'use'

    return dataset, rtype


class Handler(CORSRequestHandler):
    """API handler for all datasets."""

    def post(self):
        self.get()

    def get(self):
        try:
            path = self.request.path

            # Return API meta
            if path == '/forest-change':
                self.complete('respond', META)
                return

            dataset, rtype = _classify_request(path)

            # Unsupported dataset or reqest type
            if not dataset or not rtype:
                self.error(404)
                return

            # Handle request
            query_args = args.process(self.args(only=PARAMS[dataset][rtype]))
            path_args = args.process_path(path, rtype)
            params = dict(query_args, **path_args)

            # Queries for all require a geojson constraint for performance
            if rtype == 'all' and 'geojson' not in params:
                raise args.GeoJsonArgError()

            rid = self.get_id(params)
            target = TARGETS[dataset]
            action, data = self.get_or_execute(params, target, rid)

            # Redirect if needed
            if action != 'redirect':
                data.update(META[dataset])

            self.complete(action, data)
        except (Exception, args.ArgError), e:
            logging.exception(e)
            self.write_error(400, e.message)


handlers = webapp2.WSGIApplication([
    (r'/forest-change.*', Handler)],
    debug=True)
