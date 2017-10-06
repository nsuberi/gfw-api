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

## Updated instructions 6th October 2017
### Deploying the API via gcloud

The old API runs on Google Cloud  (app engine)

To run locally and deploy this service you will need to Download and install the [google-cloud-sdk](https://cloud.google.com/sdk/).

Next, ensure that the gcloud tool is on path.
```bash
$gcloud --version

Google Cloud SDK 174.0.0
app-engine-python 1.9.61
bq 2.0.27
core 2017.10.02
gcloud
gsutil 4.27
```

If you have installed the SDK but got no response from `gcloud --version`, then you will need to add gcloud to path:

```alias gcloud=/Users/Ben/google-cloud-sdk/bin/gcloud```

Run `glcoud init`  and configure the project.

Confirm your account is configured via `cdloud info`. You will need your account to be associated
with an account authorised to deploy to the app engine.

If you want to run the app locally you will need to execute `dev_appserver.py .`

If dev_appserver.py is not present in the local folder, e.g.:

* First confirm the google cloud sdk is installed, and that the dev_appserver is there
ls /Users/Ben/google-cloud-sdk/bin

* Next you can alias that file into your project folder:

```alias dev_appserver.py=/Users/Ben/google-cloud-sdk/bin/dev_appserver.py```


### virtual environment

You will likely need to create a new virtual environment with python 2.7 to run this code. After pulling the repo:
```
cd gfw-api
virtualenv gfw-venv python27
source gfw-venv/bin/activate
```

### Lib folder

The Google App Engine requires that a `./lib` folder be present will ALL of the project dependencies.

To install packages via requests and ensure they go into a `./lib` folder,
pip install as `pip install requests -t lib`

To ensure all requirements go to the folder `pip install -r requirements.txt -t lib`.

However, this should not be necessary, as the lib folder exisits in the repo, and is populated correctly. The only exception is the resquests module, for that you will need to grab a specific version of the libarary and add to `./lib` as follows:

```
pip install requests==2.3 -t lib
```

### Deploying (as of October 2017)

If all works (and your account has permissions to deploy), you can deploy the app using gloud via:

`gcloud app deploy`

By default this will deploy to staging, if you want to change this behaviour edit
the `app.yaml` file and change `service: staging`  to `service: default`.

```python
runtime: python27
threadsafe: true
service: staging  #default
api_version: 1

```

Then deploy via `gcloud app deploy`




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

## Deploying (depreciated version)

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
