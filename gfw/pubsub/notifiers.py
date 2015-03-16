import webapp2
import logging
import json
import re

import arrow

from google.appengine.api import mail
from google.appengine.ext import ndb

from gfw.mailers import digest_mailer

from gfw import cdb
from gfw.forestchange import forma
from gfw.forestchange import terrai
from gfw.forestchange import quicc
from gfw.forestchange import imazon

#
# Base Notifer - Extend to send out different notifications
#
class NotiferBase(webapp2.RequestHandler):
    """ 

    NotiferBase: Base Class for Notify Classes

    --  IMPORTANT:

    Extensions of this class are **REQUIRED** to have a "createBody" method that sets
    the body text, as well as a 'subject' property


      class ExampleNotify(NotiferBase):

          subject = 'I am the email subject'

          def createBody(self, result, n, e, s):
              ... do stuff ...
              self.body = ...
    
    """
    def _center(self, geom):
        return geom['coordinates'][0][0]

    def _get_max_forma_date(self):
        sql = 'SELECT MAX(date) FROM forma_api;'
        response = cdb.execute(sql)
        if response.status_code == 200:
            max_date = json.loads(response.content)['rows'][0]['max']
            return arrow.get(max_date)

    def _period(self):
        max_forma_date = self._get_max_forma_date()
        past_month = max_forma_date.replace(months=-1)
        end = '%s-01' % max_forma_date.format('YYYY-MM')
        begin = '%s-01' % past_month.format('YYYY-MM')
        return begin, end

    def post(self):
        try:
            n = ndb.Key(urlsafe=self.request.get('notification')).get()
            if n.sent:
                logging.info("skipping notification, already sent...")
                return

            e = n.params['event']
            s = n.params['subscription']
            s['forma_date'] = self._get_max_forma_date().format('YYYY-MM-DD')
            s['begin'], s['end'] = ('2006-01-01','2015-01-01')

            digest_response = self._execute('forma',s)
            digest_response = self._execute('quicc',s,digest_response)
            digest_response = self._execute('terrai',s,digest_response)
            digest_response = self._execute('imazon',s,digest_response)

            if self._has_response(digest_response):
                self.createBody(digest_response, n, e, s)
                to = s['email']
                logging.info('E %s' % e)
                if 'dry_run' in e:
                    # eightysteele@gmail.com,asteele.wri.org
                    tester, subscriber = e['dry_run'].split(',')
                    logging.info('PUB DRYRUN tester=%s subscriber=%s to=%s' %
                                (tester, subscriber, to))
                    if subscriber == to:
                        to = tester
                        logging.info('PUB DRYRUN sending email to %s' % to)
                    else:
                        return

                mail.send_mail(
                    sender='noreply@gfw-apis.appspotmail.com',
                    to=to,
                    subject=self.subject,
                    body=self.body,
                    html=self.body)
                n.sent = True
                n.put()


        except Exception, e:
            logging.exception(e)


    def _execute(self,module_name,data,digest={}):
        data_copy = data.copy()
        data_copy['geojson'] = json.dumps(data_copy['geom'])
        try:
            action, response = eval(module_name).execute(data_copy)
            digest[module_name]={}
            digest[module_name] = response
            return digest
        except:
            raise Exception('CartoDB Failed (status=%s, content=%s, alert_type=%s)' %
                           (response.status_code, response.content, module_name))

    def _has_response(self,digest):
        total = int(digest['forma'].get('value') or 0)
        total += int(digest['quicc'].get('value') or 0)
        total += int(digest['terrai'].get('value') or 0)
        return total > 0



#
# Digest Notifer: Send Diget Email 
#
class DigestNotifer(NotiferBase):

    mailer = digest_mailer

    subject = 'New Alerts from Global Forest Watch'

    def createBody(self, digest, n, e, s):
        self.body = self.mailer.intro
        for key, value in digest.iteritems():
            self._addValueSummary(key,value,n,e,s)
        self.body += self.mailer.outro

    def _addValueSummary(self,key,result,n,e,s):
        begin, end = self._period()
        result['end'] = end
        result['begin'] = begin
        result['interval'] = 'month'
        result['name'] = key
        logging.info(s)

        if result.get('value'): 
            if not result['value']:
                result['value'] = 0

            if 'geom' in s:
                result['aoi'] = 'a user drawn polygon'
                lat, lon = self._center(s['geom'])
                result['lat'] = lat
                result['lon'] = lon
                result['geom'] = s['geom']
                result['link'] = self.mailer.link_geom.format(**result)
            else:
                result['aoi'] = 'a country (%s)' % s['iso']
                result['iso'] = s['iso'].upper()
                result['link'] = self.mailer.link_iso.format(**result)
            result['link'] = re.sub('\s+', '', result['link']).strip()

            if type(result['value']) is list:
                self.body += self.mailer.list_summary_lead.format(**result)
                for result_row in result['value']:
                    self.body += self.mailer.list_summary_row.format(**result_row)

            else:
                self.body += self.mailer.summary.format(**result)

        else:
            result['params'] = json.dumps(result['params'])
            self.body += self.mailer.dump_summary.format(**result)


