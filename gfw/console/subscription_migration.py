# -- launch shell
# remote_api_shell.py -s server
#
# example:
#
# import gfw.console.subscription_migration as migration
# migration.get_old_subscriptions()
# migration.create_migrations()
#

import copy
import json
import traceback

from google.appengine.ext import ndb
from google.appengine.api import urlfetch

from gfw.models.subscription import Subscription
from gfw.v2.migrations.migration import Migration

from appengine_config import runtime_config

def count_subscriptions(topic=None):
    if topic:
        print Subscription.query(Subscription.topic == topic).count()
    else:
        print Subscription.query().count()

def create_migrations():
    return Migration.create_from_subscriptions()

def send_migration_email(migration):
    print "#####"
    print "Sending migration {0} for {1}".format(migration.key.urlsafe(), migration.email)

    migration_url = '%s/v2/migrations/%s/migrate' % \
        (runtime_config['APP_BASE_URL'], str(migration.key.urlsafe()))

    template_content = []
    message = {
        'global_merge_vars': [{
            'content': migration_url, 'name': 'migration_link'
        }],
        'to': [{
            'email': migration.email,
            'name': migration.email,
            'type': 'to'
        }],
        'track_clicks': True,
        'merge_language': 'handlebars',
        'track_opens': True
    }

    mandrill_key = runtime_config.get('mandrill_api_key')
    mandrill_url = "https://mandrillapp.com/api/1.0/messages/send-template.json"

    payload = {
        "template_content": [],
        "template_name": 'subscription-migration',
        "message": message,
        "key": mandrill_key,
        "async": "false"
    }

    result = urlfetch.fetch(mandrill_url,
                            payload=json.dumps(payload),
                            method=urlfetch.POST,
                            headers={'Content-Type': 'application/json'})

    print "Sent!"
    print result

def send_migration_emails():
    migrations = Migration.query()
    for migration in migrations.iter():
        try:
            send_migration_email(migration)
        except Exception as e:
            print "Failed"
            print migration.key.urlsafe()
            print str(e)
            traceback.print_exc()

def create_migration_for_email(email):
    print 'Creating migration for ' + email
    print Migration.create_for_email(email)
