#! sh

# download and install Google App Engine Python SDK
wget https://storage.googleapis.com/appengine-sdks/featured/google_appengine_1.9.6.zip
sudo unzip -q -d /usr/local/ google_appengine_1.9.6.zip

pip install -r requirements.txt