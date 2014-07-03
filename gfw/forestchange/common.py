
import json
import logging

from gfw import cdb


def classify_query(args):
    if 'iso' in args and not 'id1' in args:
        return 'iso'
    elif 'iso' in args and 'id1' in args:
        return 'id1'
    elif 'use' in args:
        return 'use'
    elif 'pa' in args:
        return 'pa'
    elif 'wdpaid' in args:
        return 'wdpa'
    else:
        return 'world'


class SqlError(ValueError):
    def __init__(self, msg):
        super(SqlError, self).__init__(msg)


class Sql(object):

    @classmethod
    def get_query_type(cls, params, args, the_geom_table=''):
        """Return query type (download or analysis) with updated params."""
        query_type = 'analysis'
        if 'format' in args:
            query_type = 'download'
            if args['format'] != 'csv':
                the_geom = ', the_geom' \
                    if not the_geom_table \
                    else ', %s.the_geom' % the_geom_table
                params['the_geom'] = the_geom
        return query_type, params

    @classmethod
    def process(cls, args):
        begin = args['begin'] if 'begin' in args else '2000-01-01'
        end = args['end'] if 'end' in args else '2015-01-01'
        params = dict(begin=begin, end=end, geojson='', the_geom='')
        classification = classify_query(args)
        if hasattr(cls, classification):
            return getattr(cls, classification)(params, args)


class CartoDbExecutor():

    @classmethod
    def _query_response(cls, response, params, query):
        """Return world response."""
        if response.status_code == 200:
            rows = json.loads(response.content)['rows']
            if rows:
                result = {'rows': rows}
            else:
                result = {}
            result['params'] = params
            if 'geojson' in params:
                result['geojson'] = json.loads(params['geojson'])
            if 'dev' in params:
                result['dev'] = {'sql': query}
            return result
        else:
            logging.info(query)
            raise Exception(response.content)

    @classmethod
    def execute(cls, args, sql):
        try:
            query = sql.process(args)
            if 'format' in args:
                return 'redirect', cdb.get_url(query, args)
            else:
                action, response = 'respond', cdb.execute(query)
                return action, cls._query_response(response, args, query)
        except SqlError, e:
            return 'error', e
