# -- launch shell
# remote_api_shell.py -s dev.gfw-apis.appspot.com
# import gfw.console.pubsub

from gfw.pubsub.event import Event
from gfw.pubsub.notification import Notification
from gfw.pubsub.subscription import Subscription

#
# PUBLISHING
#
def publish(**params):
    # Force DryRun unless explicitly False
    dry_run = params.get('dry_run')
    if (dry_run == None):
      dry_run = "bguzder-williams@wri.org,bguzder.wri.org"
    topic = params.get('topic')
    event = Event.publish(topic,params,dry_run)
    print "topic: %s, dry_run: %s, params: %s, event: %s" % (topic,dry_run,params,event)

#
# SUBSCRIBE 
#
def subscribe(**params):
  auto_confirm = params.pop('auto_confirm',False)
  token = Subscription.subscribe(params)
  if token and auto_confirm:
    confirm(token)
  return token

def confirm(token):
  return Subscription.confirm(token)

def unsubscribe(token):
  return Subscription.unsubscribe(token)

#
# INSPECT/RESET
#
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
  subs = Subscription.with_confirmation()
  for s in subs:
    print("%s" % s)

def unconfirmed():
  subs = Subscription.without_confirmation()
  for s in subs:
    print("%s" % s)

def printUpdates():
  subs = Subscription.query()
  for s in subs:
    print("s %s" % s.updates)