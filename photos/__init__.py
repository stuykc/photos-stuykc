import os, jinja2
from google.appengine.ext import blobstore, db

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'])

class Media(db.Model):
    name = db.StringProperty()
    stuyId = db.StringProperty()
    email = db.StringProperty()
    event = db.StringProperty()
    blob_key = blobstore.BlobReferenceProperty()
