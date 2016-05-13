[![Build Status](https://travis-ci.org/wri/gfw-api.svg?branch=feature%2Fv1)](https://travis-ci.org/wri/gfw-api)
[![Code Health](https://landscape.io/github/wri/gfw-api/feature/v1/landscape.png)](https://landscape.io/github/wri/gfw-api/feature/v1)

# Global Forest Watch API

## Developing

The API rides on [Google App Engine](https://developers.google.com/appengine)
Python 2.7 runtime, so we just need to
[download](https://developers.google.com/appengine/downloads) the latest Python
SDK (grab the Linux version) and add it to our PATH.

Then checkout the repo:

```bash
$ git clone git@github.com:wri/gfw-api.git
```

Developers Note: If you are developing you'll also need the following files
added to project root: privatekey.pem, ee_assest_ids.json, prod.json, dev.json.
Please contact Adam Mulligan or David Gonzalazez for this.

We can now run it locally using the development server that ships with App Engine:

```shell
cd gfw-api
pip install -r requirements.txt.
dev_appserver.py .
```

It's now running locally at [http://localhost:8080](http://localhost:8080) and
you get an admin console at
[http://localhost:8080/_ah/admin](http://localhost:8080/_ah/admin). Here's an
example call:

[http://localhost:8080/forest-change/umd-loss-gain/use/oilpalm/1930?thresh=10&period=2008-01-01,2013-01-01](http://localhost:8080/forest-change/umd-loss-gain/use/oilpalm/1930?thresh=10&period=2008-01-01,2013-01-01)

## Testing

We use [Nose](https://nose.readthedocs.org/en/latest/) which extends Python's
unittest functionality to make things easier. First install the requirements:

Now we can run all the tests:

```shell
nosetests --with-gae --without-sandbox test/
```

Alternatively we can run a specific test:

```
nosetests --with-gae --without-sandbox test/gfw/forestchange/api_test.py
```

## Deploying

To deploy to App Engine:

### Production

```shell
appcfg.py update -V master -M default --oauth2 .
```

### Staging

```shell
appcfg.py update -V develop -M staging --oauth2 .
```

# Backups

Backups of Subscriptions in the Google Cloud Datastore are run automatically
every 12 hours, and are stored in a Google Cloud Storage You can change this
time schedule in `cron.yaml`.

This document is useful if you need to make any changes:
https://cloud.google.com/appengine/articles/scheduled_backups?hl=en
