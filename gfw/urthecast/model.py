from google.appengine.ext import ndb

class TilesUC(ndb.Model):
	tiles_key = ndb.StringProperty()
	when_cached = ndb.DateTimeProperty(auto_now_add=True)
	data = ndb.BlobProperty()

	@classmethod
	

