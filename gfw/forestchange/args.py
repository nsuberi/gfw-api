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

"""This module provides URL argument processing and errors."""

import datetime
import json


def process_path(path, *params):
    return PathProcessor.process(path, params)


def process(args):
    return ArgProcessor.process(args)


class ArgError(ValueError):
    def __init__(self, msg):
        super(ArgError, self).__init__(msg)


class IsoArgError(ArgError):
    USAGE = """iso must be three characters."""

    def __init__(self):
        msg = 'Invalid iso parameter! Usage: %s' % self.UseArgError
        super(IsoArgError, self).__init__(msg)


class Id1ArgError(ArgError):
    USAGE = """id1 must be an integer."""

    def __init__(self):
        msg = 'Invalid id1 parameter! Usage: %s' % self.UseArgError
        super(Id1ArgError, self).__init__(msg)


class UseIdArgError(ArgError):
    USAGE = """useid must be an integer."""

    def __init__(self):
        msg = 'Invalid useid parameter! Usage: %s' % self.UseIdArgError
        super(UseIdArgError, self).__init__(msg)


class PeriodArgError(ArgError):
    USAGE = """begin,end dates in format YYYY-MM-DD."""

    def __init__(self):
        msg = 'Invalid period parameter! Usage: %s' % self.USAGE
        super(PeriodArgError, self).__init__(msg)


class GeoJsonArgError(ArgError):
    USAGE = """Valid Polygon or MultiPolygon GeoJSON string."""

    def __init__(self):
        msg = 'Invalid geojson parameter! Usage: %s' % self.USAGE
        super(GeoJsonArgError, self).__init__(msg)


class DownloadArgError(ArgError):
    USAGE = """filename.{csv | kml | shp | geojson | svg}"""

    def __init__(self):
        msg = 'Invalid download parameter! Usage: %s' % self.USAGE
        super(DownloadArgError, self).__init__(msg)


class UseArgError(ArgError):
    USAGE = """{logging | mining | oilpalm | fiber},polygonid"""

    def __init__(self):
        msg = 'Invalid use parameter! Usage: %s' % self.USAGE
        super(UseArgError, self).__init__(msg)


class WdpaIdArgError(ArgError):
    USAGE = """wdpaid must be an integer"""

    def __init__(self):
        msg = 'Invalid wdpaid parameter! Usage: %s' % self.USAGE
        super(WdpaIdArgError, self).__init__(msg)


class PathProcessor():
    @classmethod
    def iso(cls, path):
        try:
            return path.split('/')[4]
        except:
            raise Exception('Unable to process iso from request path')

    @classmethod
    def id1(cls, path):
        try:
            return path.split('/')[5]
        except:
            raise Exception('Unable to process id1 from request path')

    @classmethod
    def wdpaid(cls, path):
        try:
            return path.split('/')[4]
        except:
            raise Exception('Unable to process wpdaid from request path')

    @classmethod
    def use(cls, path):
        try:
            return path.split('/')[4]
        except:
            raise Exception('Unable to process nameid from request path')

    @classmethod
    def useid(cls, path):
        try:
            return path.split('/')[5]
        except:
            raise Exception('Unable to process nameid from request path')

    @classmethod
    def process(cls, path, params):
        """Process parameter from supplied request path"""
        result = {}
        for param in params:
            if hasattr(cls, param):
                result.update({param: getattr(cls, param)(path)})
        return result


class ArgProcessor():

    @classmethod
    def period(cls, value):
        try:
            begin, end = value.split(',')
            f = datetime.datetime.strptime
            b, e = f(begin, '%Y-%m-%d'), f(end, '%Y-%m-%d')
            if b > e:
                raise
            return dict(begin=begin, end=end)
        except:
            raise PeriodArgError()

    @classmethod
    def iso(cls, value):
        try:
            if len(value) != 3:
                raise
            return dict(iso=value)
        except:
            raise PeriodArgError()

    @classmethod
    def id1(cls, value):
        try:
            int(value)
            return dict(id1=value)
        except:
            raise PeriodArgError()

    @classmethod
    def geojson(cls, value):
        try:
            geom = json.loads(value)
            if geom['type'] != 'Polygon' and geom['type'] != 'MultiPolygon':
                raise
            return {'geojson': value}
        except:
            raise GeoJsonArgError()

    @classmethod
    def download(cls, value):
        try:
            filename, fmt = value.split('.')
            if not filename or not fmt:
                raise
            return dict(format=fmt, filename=filename)
        except:
            raise DownloadArgError()

    @classmethod
    def use(cls, value):
        try:
            if not value in ['logging', 'mining', 'oilpalm', 'fiber']:
                raise
            return dict(use=value)
        except:
            raise UseArgError()

    @classmethod
    def useid(cls, value):
        try:
            int(value)
            return dict(useid=value)
        except:
            raise UseIdArgError()

    @classmethod
    def wdpaid(cls, value):
        try:
            int(value)
            return dict(wdpaid=value)
        except:
            raise WdpaIdArgError()

    @classmethod
    def bust(cls, value):
        return dict(bust=True)

    @classmethod
    def dev(cls, value):
        return dict(dev=True)

    @classmethod
    def process(cls, args):
        """Process supplied dictionary of args into new dictionary of args."""
        processed = {}
        if not args:
            return processed
        for name, value in args.iteritems():
            if hasattr(cls, name):
                processed.update(getattr(cls, name)(value))
        return processed
