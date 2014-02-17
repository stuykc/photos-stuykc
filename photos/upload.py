from photos import JINJA_ENVIRONMENT, Photo
import webapp2
from google.appengine.ext import blobstore, db
from google.appengine.ext.webapp import blobstore_handlers

class UploadForm(webapp2.RequestHandler):

    def get(self):
        upload_url = blobstore.create_upload_url('/success')

        template_values = {
            'upload_url': upload_url
        }

        template = JINJA_ENVIRONMENT.get_template('upload.html')
        self.response.write(template.render(template_values))

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):

    def get(self):
        self.redirect('/upload')

    def post(self):
        name = self.request.get('name')
        stuyId = self.request.get('id')
        email = self.request.get('email')
        event = self.request.get('event')
        upload = self.get_uploads()
        for photo in upload:
            uploaded_photo = Photo(name=name, stuyId=stuyId, email=email, event=event, blob_key=photo.key())
            db.put(uploaded_photo)
        
        template_values = {
            'event': event
        }

        template = JINJA_ENVIRONMENT.get_template('success.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/upload', UploadForm),
    ('/success', UploadHandler)
], debug=True)
