import webapp2
import logging
import json
import re

import arrow

from google.appengine.api import mail
from google.appengine.ext import ndb

from gfw.mailers import digest_mailer

from gfw import cdb
from gfw.pubsub.subscription import Subscription
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
    sqls = {
        'forma': forma.FormaSql,
        'terrai': terrai.TerraiSql,
        'imazon': imazon.ImazonSql,
        'quicc': quicc.QuiccSql
    }

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
            s = self._prepSubscription(n.params['subscription'],n.params['updates'],begin,end)

            formaData = self._moduleData(s,{
                    'name': 'forma',
                    'url_id': 'forma',
                    'email_name': 'FORMA',
                    'summary':'Detects areas where tree cover loss is likely to have recently occurred',
                    'specs':'monthly, 500m, humid tropics, WRI/CGD'
                })
            # terraiData = self._moduleData(s,{
            #         'name': 'terrai',
            #         'url_id': 'terrailoss',
            #         'email_name': 'Terra-i',
            #         'summary':'Detects areas in Latin American where tree cover loss is likely to have recently occurred',
            #         'specs':'monthly, 250m, Latin America, CIAT',
            #     })
            imazonData = self._moduleData(s,{
                    'name': 'imazon',
                    'url_id': 'imazon',
                    'email_name': 'SAD',
                    'summary':'Detects forest cover loss and forest degradation in the Brazilian Amazon',
                    'specs':'monthly, 250m, Brazilian Amazon, Imazon',
                    'value_names': {
                        'degrad': 'hectares degradation',
                        'defor': 'hectares deforestation'
                    }
                })    

            max_quicc_date = self._get_max_date('quicc')
            force_min_date, force_max_date, quicc_interval = self._period(max_quicc_date,3,True)        
            quiccData = self._moduleData(s,{
                    'name': 'quicc',
                    'url_id': 'modis',
                    'email_name': 'QUICC',
                    'summary':'Identifies areas of land that have lost at least 40% of their green vegetation cover from the previous quarterly product',
                    'specs':'quarterly, 5km, <37 degrees north, NASA'
                },True,force_min_date,force_max_date)
            storiesData = self._storiesData(s,{
                    'name': 'stories',
                    'url_id': 'none/580',
                    'summary':'Forest-related stories reported by GFW users',
                    'specs':'',
                    'email_name': 'Stories'
                })


            if self.total_alerts > 0:
                #
                # create email
                #
                self.body = self.mailer.intro
                self.body += self.mailer.header.format(selected_area_name=s['aoi'])
                self.body += self.mailer.table_header
                self.body += self._alert(formaData)
                # self.body += self._alert(terraiData)
                self.body += self._alert(imazonData)
                self.body += self._alert(storiesData)                
                self.body += self._alert(quiccData)
                self.body += self.mailer.table_footer
                self.body += self.mailer.outro.format(**s)
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print self.body
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                print " "
                #
                # send email
                #
                to = s['email']
                dry_run = e.get('dry_run')
                if dry_run:
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
                self._updateSubscriptionDates(n.params['subscription_id'])

        except Exception, e:
            logging.exception(e)



    #
    # Dates
    #

    def _updateSubscriptionDates(self,subscription_id):
        subscription = Subscription.get_by_id(subscription_id)
        updated = None
        for key in self.sqls:
            date = self._recentDate(key,0)
            if date:
                updated = True
                if not subscription.updates:
                    subscription.updates = {}
                subscription.updates[key] = date
        if updated:
            subscription.put()

    def _latestSQL(self,name,limit):
        sql_model = self.sqls.get(name)
        if sql_model:
            return sql_model.LATEST.format(limit=limit)


    def _recentDate(self,name,nth=1):
        date = None
        sql = self._latestSQL(name,nth+1)
        
        if name == "stories":
            name = "forma"

        if sql:
            response = cdb.execute(sql)
            if response.status_code == 200:
                last_date = json.loads(response.content)['rows'][nth]['date']
                if last_date:
                    date = arrow.get(last_date).replace(days=+1)
        if not date:
            date = arrow.now().replace(months=-2)

        return date.format("YYYY-MM-DD")

    def _beginDate(self,data,module_info):
        date = None
        updates = data.get("updates")
        name = module_info["name"]
        if updates:
            last_update = updates.get(name)
            if last_update:
                date = arrow.get(last_update).replace(days=+1).format("YYYY-MM-DD")
        if not date:
            date = self._recentDate(name)
        return date

    #
    # Module Data
    #  

    def _prepSubscription(self,sub,updates,begin,end):
        if 'geom' in sub:
            sub['geojson'] = json.dumps(sub['geom'])
            sub['aoi'] = 'a user drawn polygon'
        else:
            if sub.get('iso'):
                sub['iso'] = sub['iso'].upper()
                if sub.get('id1'):
                    href = self.mailer.link_country_id1.format(iso=sub['iso'],id1=sub['id1'])
                    link_text = '%s/%s' % (sub['iso'],sub['id1'])
                    template = 'a subnational-region (%s)'
                else:
                    href = self.mailer.link_country_iso.format(iso=sub['iso'])
                    link_text = '%s' % (sub['iso'])
                    template = 'a country (%s)'
                link = "<a href='%s'>%s</a>" % (href,link_text)
                sub['aoi'] = template % link

            else:
                raise Exception('Invalid Subscription (data=%s)' %
                           (sub)) 

        sub['alert_query'] = True
        sub['begin'] = begin.format('YYYY-MM-DD')
        sub['end'] = end.format('YYYY-MM-DD')
        sub['updates'] = updates
        logging.info(sub)
        return sub

    def _prepData(self,data,module_info):
        data = data.copy()
        data['end'] = arrow.now().format("YYYY-MM-DD")
        data['begin'] = self._beginDate(data,module_info)
        data['url_id'] = module_info.get('url_id')
        return data

    def _moduleData(self,sub,module_info,increment_value=True,force_min_date=None,force_max_date=None):
        data = self._prepData(sub,module_info)
        try:

            action, response = eval(module_info.get('name')).execute(data)
            total_value, alerts, alert_types, min_date, max_date = self._valueAndAlerts(response,module_info.get('value_names'))
            if force_max_date:
                if (min_date <= force_max_date):
                    module_info['min_date'] = force_min_date
                    module_info['max_date'] = force_max_date
                else:
                    return None
            else:
                if min_date:
                    module_info['min_date'] = min_date.split('T')[0]
                elif total_value > 0:
                    module_info['min_date'] =  data.get('begin')
                else:
                    module_info['min_date'] = ""


                if max_date:
                    module_info['max_date'] = max_date.split('T')[0]
                elif total_value > 0:
                    module_info['max_date'] = data.get('end')
                else:
                    module_info['max_date'] = ""





            data['min_date'] = module_info['min_date']
            data['max_date'] = module_info['max_date']
            module_info['url'] = self._linkUrl(data)

            module_info['date_range'] = self._dateRange(module_info)
            module_info['alerts'] = alerts
            module_info['alert_types'] = alert_types

            if total_value > 0:
                if increment_value:
                    self.total_alerts += total_value
                return module_info       
            else:
                return None
                
        except Exception, e:
            raise Exception('ERROR[_moduleData] (error=%s, module_info=%s, data=%s)' %
                           (e,module_info,data))  

    def _dateRange(self,module_info):
        if module_info['min_date'] == module_info['max_date']:
            date_range = module_info['min_date']
        else:
            date_range = "%s to %s" % (module_info['min_date'],module_info['max_date'])
        return date_range

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
                data['geom'] = json.dumps(data['geom'])
                link = self.mailer.link_geom.format(**data)
            else:
                link = self.mailer.link_iso.format(**data)

            safe_link = re.sub('\s+', '', link).strip()
            return safe_link

    def _valueAndAlerts(self,response,value_names={}):
        value = 0
        alerts = ''
        alert_types = ''
        response_val = response.get('value')
        min_date = response.get('min_date')
        max_date = response.get('max_date')
        if response_val:
            if type(response_val) is list:
                for v_dict in response_val:
                    if not max_date:
                        min_date = v_dict.get('min_date')
                        max_date = v_dict.get('max_date')
                    v = int(v_dict.get('value') or 0)
                    if (v > 0):
                        if value > 0:
                            alerts += '/'
                            alert_types += '/'
                        alert_name = value_names.get(v_dict.get('data_type')) or v_dict.get('data_type')
                        value += v
                        alerts += '%s' % (v)
                        alert_types += '%s' % (alert_name)
                if value:
                    alert_types = "( %s )" % alert_types

            else:
                alert_name = value_names or 'alerts'
                if type(response_val) is dict:
                    value = response_val.get('value')
                else:
                    value = int(response_val)
                alerts = '%s' % (value)

        return value, alerts, alert_types, min_date, max_date

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
                module_info['date_range'] = self._dateRange(module_info)           
                module_info['url'] = self._linkUrl(data)
                module_info['alerts'] = '%s' % (stories_count)                
                module_info['alert_types'] = ''                
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
            'terrai':'latin_decrease_current_points',
            'imazon':'imazon_sad',
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
        return self.mailer.table_row.format(**data)            


