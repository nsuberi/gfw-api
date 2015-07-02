# -- launch shell
# remote_api_shell.py -s dev.gfw-apis.appspot.com
# import gfw.console.pubsub as ps
import json

from google.appengine.ext import ndb
import arrow

from gfw.pubsub.event import Event
from gfw.pubsub.notification import Notification
from gfw.pubsub.subscription import Subscription

#
# PUBLISHING
#

drb = "bguzder-williams@wri.org,bguzder.wri.org"
dra = "abarrett@wri.org,bguzder.wri.org"
dr8 = "asteele@wri.org,bguzder.wri.org"

def publish(**params):
    # Force DryRun unless explicitly False
    dry_run = params.get('dry_run')
    if (dry_run == None):
      dry_run = "bguzder-williams@wri.org,bguzder.wri.org"
    topic = params.get('topic')
    event = Event.publish(topic,params,dry_run)
    print "topic: %s, dry_run: %s, params: %s, event: %s" % (topic,dry_run,params,event)

#
# REPORTING
#
def report(begin=None,end=None):
  rpt = report_dict(begin,end)
  confirmed_subscriptions = ""
  for sub in rpt['filtered']['confirmed']['subscriptions']:
    confirmed_subscriptions += "        %s, %s, %s\n" % (sub)
  unconfirmed_subscriptions = ""
  for sub in rpt['filtered']['unconfirmed']['subscriptions']:
    unconfirmed_subscriptions += "        %s, %s, %s\n" % (sub)

  rpt_params = {
    'begin':rpt['filtered']['begin'],
    'end':rpt['filtered']['end'],
    'confirmed_count':rpt['total']['confirmed'],
    'unconfirmed_count':rpt['total']['unconfirmed'],
    'filtered_confirmed_count':rpt['filtered']['confirmed']['count'],
    'filtered_unconfirmed_count':rpt['filtered']['unconfirmed']['count'],
    'confirmed_subscriptions':confirmed_subscriptions,
    'unconfirmed_subscriptions':unconfirmed_subscriptions
  }

  rpt_str = """
    Subscription API Report --

    Totals:
      confirmed:{confirmed_count}
      unconfirmed: {unconfirmed_count}

    Filtered[{begin} to {end}]:
      confirmed: {filtered_confirmed_count}
      unconfirmed: {filtered_unconfirmed_count}

    Subscriptions:
      confirmed:\n{confirmed_subscriptions}
      unconfirmed:\n{unconfirmed_subscriptions}
  """
  return rpt_str.format(**rpt_params)



def report_dict(begin=None,end=None):
  if not end:
    end = arrow.now().format('YYYY-MM-DD')
  rpt = {}
  confirmed = Subscription.query(Subscription.confirmed==True)
  unconfirmed = Subscription.query(ndb.OR(Subscription.confirmed==False,Subscription.confirmed==None))
  rpt['total'] = {
    'confirmed': confirmed.count(),
    'unconfirmed': unconfirmed.count()
  }
  def sub_tuple(sub):
    params=sub.params
    typ = params.get('iso','geojson')
    date = arrow.get(sub.created).format("YYYY-MM-DD")
    return (typ,date,sub.email)

  if begin:
    filtered_confirmed = filter_subscriptions(confirmed,begin,end)
    filtered_unconfirmed = filter_subscriptions(unconfirmed,begin,end)
    rpt['filtered'] = {
      'begin': begin,
      'end': end
    }
    rpt['filtered']['confirmed'] = {
      'count': filtered_confirmed.count(),
      'subscriptions': map(sub_tuple,filtered_confirmed)
    }
    rpt['filtered']['unconfirmed'] = {
      'count': filtered_unconfirmed.count(),
      'subscriptions': map(sub_tuple,filtered_unconfirmed)
    }
  return rpt


#
# INSPECT/RESET
#
def filter_subscriptions(subscriptions,begin=None,end=None):
  if begin:
    begin_date = arrow.get(begin).datetime
    filtered_subscriptions = subscriptions.filter(Subscription.created>=begin_date)
    if end:
      end_date = arrow.get(end).datetime
    else:
      end_date = arrow.now().datetime
    filtered_subscriptions = subscriptions.filter(Subscription.created<=end_date)
    return filtered_subscriptions
  else:
    return subscriptions


def resetUpdates():
  subs = Subscription.query()
  for s in subs:
    if s.updates:
      print("s %s" % s.email)
      s.updates = None
      s.put()

def checkSubs(email=None):
  if not email:
    email = 'bguzder.wri.org'
  subs = Subscription.query(Subscription.email==email)
  for s in subs:
      print("check sub:  %s" % s)

def clearSubs(email=None):
  if not email:
    email = 'bguzder.wri.org'
  subs = Subscription.query(Subscription.email==email)
  for s in subs:
      print("clear sub:  %s" % s)
      s.updates = None
      s.put()

def confirmed():
  subs = Subscription.get_confirmed()
  for s in subs:
    print("%s" % s)

def printUpdates():
  subs = Subscription.query()
  for s in subs:
    print("s %s" % s.updates)