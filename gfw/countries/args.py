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

"""This module provides URL argument processing for countries API."""


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


class ThreshArgError(ArgError):
    USAGE = """thresh must be either 10, 15, 20, 25, 30, 50, 75"""

    def __init__(self):
        msg = 'Invalid wdpaid parameter! Usage: %s' % self.USAGE
        super(ThreshArgError, self).__init__(msg)


class PathProcessor():
    @classmethod
    def iso(cls, path):
        try:
            return dict(iso=path.split('/')[2])
        except:
            raise Exception('Unable to process iso from request path')

    @classmethod
    def id1(cls, path):
        try:
            arg = dict(id1=path.split('/')[3])
            arg.update(cls.iso(path))
            return arg
        except:
            raise Exception('Unable to process id1 from request path')

    @classmethod
    def process(cls, path, params):
        """Process parameter from supplied request path"""
        result = {}
        for param in params:
            if hasattr(cls, param):
                result.update(getattr(cls, param)(path))
        return result


class ArgProcessor():

    @classmethod
    def thresh(cls, value):
        try:
            if int(value) in [10, 15, 20, 25, 30, 50, 75]:
                return dict(thresh=value)
            else:
                raise
        except:
            raise ThreshArgError()

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
