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
            min_alert_dates = e.get('min_alert_dates')                
            begin, end = self._digestDates(e)
            s = self._prepSubscription(n.params['subscription'],begin,end)

            formaData = self._moduleData(s,{
                    'name': 'forma',
                    'url_id': 'forma',
                    'link_text': 'FORMA',
                    'description':'monthly, 500m, humid tropics, WRI/CGD'
                },min_alert_dates)
            terraiData = self._moduleData(s,{
                    'name': 'terrai',
                    'url_id': 'terrailoss',
                    'link_text': 'Terra-i',
                    'description':'monthly, 250m, Latin America, CIAT',
                    'additional_select':', MIN(grid_code) as min_grid_code, MAX(grid_code) as max_grid_code'
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
                },min_alert_dates)            

            max_quicc_date = self._get_max_date('quicc')
            quicc_begin, quicc_end, quicc_interval = self._period(max_quicc_date,3,True)
            quiccData = self._moduleData(s,{
                    'name': 'quicc',
                    'url_id': 'modis',
                    'link_text': 'QUICC',
                    'description':'quarterly, 5km, <37 degrees north, NASA',
                    'begin': quicc_begin,
                    'end': quicc_end
                },min_alert_dates,False)
            
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
                self.body += self.mailer.header.format(**s)
                self.body += self._alert(formaData)
                self.body += self._alert(terraiData)
                self.body += self._alert(imazonData)
                self.body += self._alert(storiesData)                

                if quiccData:
                    self.body += self.mailer.quicc_leader.format(**quiccData)               
                    self.body += self._alert(quiccData)

                self.body += self.mailer.outro.format(**s)


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
    # Dates
    #

    def _latestSQL(self,name):
        sqls = {
            'forma': forma.FormaSql,
            'terrai': terrai.TerraiSql,
            'imazon': imazon.ImazonSql,
            'quicc': quicc.QuiccSql
        }
        return sqls.get(name).LATEST.format(limit=2)


    def _recentDate(self,name):
        sql = self._latestSQL(name)
        response = cdb.execute(sql)
        if response.status_code == 200:
            last_date = json.loads(response.content)['rows'][1]['date']
            if not last_date:
                return None
            else:
                return arrow.get(last_date).replace(days=+1)
        else:
            return None

    def _beginDate(self,data,module_info):
        date = None
        updates = data.get("updates")
        name = module_info["name"]
        if updates:
            last_update = updates.get(name)
            if last_update:
                date = arrow.get(last_update).replace(days=+1)
        if not date:
            date = self._recentDate(name)
        return date.format("YYYY-MM-DD")

    #
    # Module Data
    #  

    def _prepSubscription(self,sub,begin,end):
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

        sub['alert_query'] = True
        sub['begin'] = begin.format('YYYY-MM-DD')
        sub['end'] = end.format('YYYY-MM-DD')
        logging.info(sub)
        return sub

    def _prepData(self,data,module_info):
        data = data.copy()
        data['end'] = arrow.now().format("YYYY-MM-DD")
        data['begin'] = self._beginDate(data,module_info)
        data['additional_select'] = module_info.get('additional_select')
        data['url_id'] = module_info.get('url_id')
        return data

    def _moduleData(self,sub,module_info,min_alert_dates=None,increment_value=True):
        data = self._prepData(sub,module_info)
        if min_alert_dates:
            min_alert_date = min_alert_dates.get(module_info['name'])
            if min_alert_date:
                data['min_alert_date'] = min_alert_date

        try:
            action, response = eval(module_info.get('name')).execute(data)
            total_value, alerts, mindate, maxdate = self._valueAndAlerts(response,module_info.get('value_names'))
            if module_info.get('begin') and module_info.get('end'):
                data['min_date'] = data['begin'] 
                data['max_date'] = data['end'] 
            else:
                min_date, max_date = self._minMaxDates(response,mindate,maxdate)
                data['min_date'] = min_date or data['begin'] 
                data['max_date'] = max_date or data['end'] 

            module_info['min_date'] = data['min_date']
            module_info['max_date'] = data['max_date']
            url = self._linkUrl(data)
            module_info['url'] = url
            module_info['alerts'] = alerts
            if total_value > 0:
                if increment_value:
                    self.total_alerts += total_value
                return module_info
            else:
                return None
        except Exception, e:
            raise Exception('ERROR[_moduleData] (error=%s, module_info=%s, data=%s)' %
                           (e,module_info,data))  

    def _minMaxDates(self,response,mindate,maxdate):
        min_date = mindate or response.get('min_date')
        max_date = maxdate or response.get('max_date')
        if min_date:
            min_date = arrow.get(min_date).format('YYYY-MM-DD')
        if max_date:
            max_date = arrow.get(max_date).format('YYYY-MM-DD')        
        return min_date, max_date


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
        min_date = None
        max_date = None
        if response_val:
            if type(response_val) is list:
                for v_dict in response_val:
                    if not max_date:
                        min_date = v_dict.get('min_date')
                        max_date = v_dict.get('max_date')
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


        return value, alerts, min_date, max_date

    #
    # Stories
    #
    def _storiesData(self,sub,module_info):
        data = self._prepData(sub,module_info)
        try:
            stories_count = stories.count_stories(data)
            if stories_count > 0:
                self.total_alerts += stories_count
                data['min_date'] = data['begin'] 
                data['max_date'] = data['end']                 
                module_info['min_date'] = data['min_date']
                module_info['max_date'] = data['max_date']            
                module_info['url'] = self._linkUrl(data)
                module_info['alerts'] = '%s stories' % (stories_count)                
                return module_info         
            else:
                return None
        except Exception, e:
            raise Exception('ERROR[_storiesData] (error=%s, module_info=%s, data=%s)' %
                           (e,module_info,data))
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
            date = arrow.get(max_date)            
            return date
        else:
            return arrow.now()

    def _interval(self,months):
        if months == 1:
            return 'month'
        elif months == 3:
            return 'quarterly'
        else:
            return '%s months' % months

    def _digestDates(self,event):
        event_end = event.get('end')
        event_begin = event.get('begin')
        if event_end:
            end = arrow.get(event_end)
        else:
            end = arrow.now()

        if event_begin:
            begin = arrow.get(event_begin)
        else:
            last_sent_date = self._lastSentDate()
            if last_sent_date:
                begin = arrow.get(last_sent_date)            
            else:
                begin = end.replace(months=-1)
        return begin, end

    def _lastSentDate(self):
        #
        # TODO: fetch the last day we sent out alerts
        #
        return None

    def _period(self,max_date,months=1,force_last_day=False):
        if not months:
            months = 1
        interval = self._interval(months)
        if force_last_day:
            max_date = max_date.replace(months=+1).replace(day=1).replace(days=-1)
            end = max_date.format('YYYY-MM-DD')
            begin = '%s-01' % max_date.replace(months=-1*(months-1)).format('YYYY-MM')       
        else:
            end = '%s-01' % max_date.format('YYYY-MM')
            begin = '%s-01' % max_date.replace(months=-1*months).format('YYYY-MM')       
        return begin, end, interval

    def _alert(self,data):
        if not data:
            return ""
        if data.get('description'):
            return self.mailer.alert.format(**data)            
        else:
            return self.mailer.simple_alert.format(**data)

