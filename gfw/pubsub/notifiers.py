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
from gfw import stories

#
# Base Notifer - Extend to send out different notifications
#
class DigestNotifer(webapp2.RequestHandler):
    mailer = digest_mailer
    subject = 'New Alerts from Global Forest Watch'
    total_alerts = 0

    def post(self):
        try:
            n = ndb.Key(urlsafe=self.request.get('notification')).get()
            
            if n.sent:
                logging.info("skipping notification, already sent...")
                return
            #
            # set up data
            #
            e = n.params['event']
            s = self._prepSubscription(n.params['subscription'])
            self.defaut_max_date = self._get_max_date('forma')

            formaData = self._moduleData(s,{
                    'name': 'forma',
                    'url_id': 'forma',
                    'link_text': 'FORMA',
                    'description':'monthly, 500m, humid tropics, WRI/CGD'
                })
            terraiData = self._moduleData(s,{
                    'name': 'terrai',
                    'url_id': 'terrailoss',
                    'link_text': 'Terra-i',
                    'description':'monthly, 250m, Latin America, CIAT'
                })
            imazonData = self._moduleData(s,{
                    'name': 'imazon',
                    'url_id': 'imazon',
                    'link_text': 'SAD',
                    'description':'monthly, 250m, Brazilian Amazon, Imazon',
                    'value_names': {
                        'degrad': 'hectares degradation',
                        'defor': 'hectares deforestation'
                    }
                })            
            quiccData = self._moduleData(s,{
                    'name': 'quicc',
                    'url_id': 'modis',
                    'link_text': 'QUICC',
                    'description':'quarterly, 5km, <37 degrees north, NASA',
                    'months': 3,
                    'force_last_day':True
                })
            storiesData = self._storiesData(s,{
                    'name': 'stories',
                    'url_id': 'none/580',
                    'link_text': 'User stories'
                })

            if self.total_alerts > 0:
                #
                # create email
                #
                self.body = self.mailer.intro
                self.body += self._alert(formaData)
                self.body += self._alert(terraiData)
                self.body += self._alert(imazonData)
                self.body += self._alert(quiccData)                
                self.body += self._alert(storiesData)                
                self.body += self.mailer.outro

                print(self.body)
                #
                # send email
                #
                to = s['email']
                if 'dry_run' in e:
                    # eightysteele@gmail.com,asteele.wri.org
                    tester, subscriber = e['dry_run'].split(',')
                    print "%s  %s" % (tester, subscriber)
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



  
    #
    # Module Data
    #  

    def _prepSubscription(self,sub):
        if 'geom' in sub:
            sub['geojson'] = json.dumps(sub['geom'])
            sub['aoi'] = 'a user drawn polygon'
        else:
            if sub.get('iso'):
                sub['iso'] = sub['iso'].upper()
                sub['aoi'] = 'a country (%s)' % sub['iso']
            else:
                raise Exception('Invalid Subscription (data=%s)' %
                           (sub)) 

        logging.info(sub)
        return sub

    def _moduleData(self,sub,module_info):
        max_date = self._get_max_date(module_info.get('table_name') or module_info.get('name'))
        (begin, end, interval) = self._period(
            max_date,
            module_info.get('months'),
            module_info.get('force_last_day')
        )
        data = sub.copy()
        data['end'] = end
        data['begin'] = begin
        data['interval'] = interval
        data['url_id'] = module_info['url_id']

        try:
            action, response = eval(module_info.get('name')).execute(data)
            url = self._linkUrl(data)
            total_value, alerts = self._valueAndAlerts(response,module_info.get('value_names'))
            module_info['url'] = url
            module_info['alerts'] = alerts
            if total_value > 0:
                self.total_alerts += total_value
                return module_info
            else:
                return None
        except Exception, e:
            raise Exception('CartoDB Failed (error=%s, module_info=%s)' %
                           (e,module_info))  

    def _linkUrl(self,data):
            if 'geom' in data:
                lat, lon = self._center(data['geom'])
                data['lat'] = lat
                data['lon'] = lon
                data['geom'] = data['geom']
                link = self.mailer.link_geom.format(**data)
            else:
                link = self.mailer.link_iso.format(**data)

            safe_link = re.sub('\s+', '', link).strip()
            return safe_link

    def _valueAndAlerts(self,response,value_names={}):
        value = 0
        alerts = ''
        response_val = response.get('value')

        if response_val:
            if type(response_val) is list:
                for v_dict in response_val:
                    v = int(v_dict.get('value') or 0)
                    if (v > 0):
                        if value > 0:
                            alerts += ', '
                        alert_name = value_names.get(v_dict.get('data_type')) or v_dict.get('data_type')
                        value += v
                        alerts += '%s %s' % (v, alert_name)
            else:
                alert_name = value_names or 'alerts'
                value = int(response_val)
                alerts = '%s %s' % (value, alert_name)

        return value, alerts

    #
    # Stories
    #
    def _storiesData(self,sub,module_info):
        (begin, end, interval) = self._period(self.defaut_max_date)
        data = sub.copy()
        data['end'] = end
        data['begin'] = begin
        data['interval'] = interval
        data['url_id'] = module_info['url_id']

        try:
            stories_count = stories.count_stories(data)
            if stories_count > 0:
                self.total_alerts += stories_count
                module_info['url'] = self._linkUrl(data)
                module_info['alerts'] = '%s stories' % (stories_count)   
                return module_info         
            else:
                return None
        except Exception, e:
            raise Exception('CartoDB Failed (error=%s, module_info=%s)' %
                           (e,module_info))
    #
    # Helpers
    #                 
    def _center(self, geom):
        return geom['coordinates'][0][0]

    def _get_max_date(self,name):
        alert_tables = {
            'forma':'forma_api',
            'terrai':'terra_i_decrease',
            'imazon':'imazon_clean',
            'quicc':'modis_forest_change_copy'
        }
        table_name = alert_tables.get(name) or name
        sql = 'SELECT MAX(date) FROM %s;' % table_name
        response = cdb.execute(sql)
        if response.status_code == 200:
            max_date = json.loads(response.content)['rows'][0]['max']
            date = arrow.get(max_date or self.defaut_max_date)            
            return date
        else:
            return self.defaut_max_date

    def _interval(self,months):
        if months == 1:
            return 'month'
        elif months == 3:
            return 'quarterly'
        else:
            return '%s months' % months

    def _period(self,max_date,months=1,force_last_day=False):
        if not months:
            months = 1
        interval = self._interval(months)
        if force_last_day:
            months = months - 1
        past_month = max_date.replace(months=-1*months)
        if force_last_day:
            max_date = max_date.replace(months=+1).replace(day=1).replace(days=-1)
            end = max_date.format('YYYY-MM-DD')
        else:
            end = '%s-01' % max_date.format('YYYY-MM')
        begin = '%s-01' % past_month.format('YYYY-MM')       
        return begin, end, interval

    def _alert(self,data):
        if not data:
            return ""
        if data.get('description'):
            return self.mailer.alert.format(**data)            
        else:
            return self.mailer.simple_alert.format(**data)

