# -- launch shell
# remote_api_shell.py -s server
#
# example:
#
# import gfw.console.subscription_migration as migration
# migration.get_old_subscriptions()
# migration.create_migrations()
#

from gfw.pubsub.subscription import Subscription
from google.appengine.ext import ndb
from gfw.user.gfw_user import GFWUser
from gfw.pubsub.api import notify
from gfw.pubsub.api import get_deltas
from gfw.pubsub.api import meta_str
from gfw.pubsub.api import get_meta
from gfw.pubsub.mail_handlers import send_mail_notification
from gfw.pubsub.mail_handlers import is_count_zero
from gfw.pubsub.mail_handlers import display_counts
import copy
import json
import traceback
from google.appengine.ext import ndb

def count_subscriptions():
    from gfw.pubsub.subscription import Subscription
    print Subscription.query(Subscription.topic == 'alerts/glad').count()

def for_alicia():
    #subs = Subscription.query(Subscription.user_id == ndb.Key(GFWUser, 5204238581891072))
    subs = Subscription.query(Subscription.topic == 'alerts/glad')

    dates = {
        'alerts/glad': {
            'begin': '02-26-2016',
            'end': '03-03-2016'
        },
        'alerts/treeloss': {
            'begin': '01-01-2015',
            'end': '01-01-2016'
        },
        'alerts/terra': {
            'begin': '01-01-2004',
            'end': '01-01-2016'
        },
        'alerts/prodes': {
            'begin': '01-01-2013',
            'end': '01-01-2016'
        },
        'alerts/sad': {
            'begin': '01-01-2015',
            'end': '01-01-2016'
        },
        'alerts/quicc': {
            'begin': '01-01-2015',
            'end': '01-01-2016'
        },
        'alerts/guyra': {
            'begin': '01-01-2001',
            'end': '01-01-2016'
        }
    }

    for sub in subs.iter():
      if not sub.topic in dates:
          continue
      #if not sub.topic == 'alerts/prodes':
          #continue
      params = copy.copy(sub.params)
      params['begin'] = dates[sub.topic]['begin']
      params['end'] = dates[sub.topic]['end']

      if 'geom' in params:
        geom = params['geom']
        if 'geometry' in geom:
            geom = geom['geometry']
        params['geojson'] = json.dumps(geom)

      try:
        action, data = get_deltas(sub.topic, params)
        if (is_count_zero(sub.topic, data) == False):
          print '---'
          print sub.key.id()
          print sub.email
          print sub.topic
          print display_counts(sub.topic, data)
          print '*** more than zero'
          print sub.user_id
          send_mail_notification(sub, sub.email,
                  sub.user_id.get().get_profile(), sub.topic, data,
                  meta_str(get_meta(sub.topic)))
        else:
          pass
          #print '---'
          #print sub.topic
          #print sub.url
          #print data
          #print data
      except Exception as e:
        print str(e)
        traceback.print_exc()



def list_migrations():
    subs = Subscription.query(Subscription.topic == 'alerts/glad')

    for sub in subs.iter():
        #print sub.url
        params = copy.copy(sub.params)
        params['begin'] = '02-26-2016' # mm-dd-yyyy
        params['end'] = '03-03-2016'

        if 'geom' in params:
          geom = params['geom']
          if 'geometry' in geom:
              geom = geom['geometry']
          params['geojson'] = json.dumps(geom)

        try:
          action, data = get_deltas(sub.topic, params)
          if (is_count_zero('alerts/glad', data) == False):
            print '---'
            print sub.key.id()
            print sub.email
            print sub.url
            print sub.topic
            print display_counts(sub.topic, data)
            print '*** more than zero'
          else:
            print '---'
            print sub.topic
            print data
        except Exception:
            pass
