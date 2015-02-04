#! sh

# download and install Google App Engine Python SDK
wget https://storage.googleapis.com/appengine-sdks/deprecated/1914/google_appengine_1.9.14.zip
sudo unzip -q -d /usr/local/ google_appengine_1.9.14.zip

pip install -r requirements.txt