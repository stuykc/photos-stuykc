from photos import JINJA_ENVIRONMENT, Media
import webapp2, urllib
from google.appengine.api import users, images
from google.appengine.ext import blobstore, db
from google.appengine.ext.webapp import blobstore_handlers

class AdminPage(webapp2.RequestHandler):

    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                template_values = {
                    'user': user.nickname(),
                    'logout_url': users.create_logout_url('/'),
                    'images': fetchMedias()
                }
                template = JINJA_ENVIRONMENT.get_template('admin.html')
                self.response.write(template.render(template_values))
            else:
                self.redirect('/')
        else:
            login_url = users.create_login_url('/admin')
            self.redirect(login_url)

def fetchMedias():
    media_query = Media.all().order('event')
    image_fetch = []
    for media in media_query.run():
        if media.blob_key.content_type.find('image') != -1:
            image_link = images.get_serving_url(media.blob_key)
            image_link_thumb = image_link + '=s150-c'
            image_link_full = image_link + '=s0'
        else:
            image_link_thumb = image_link_full = '/admin/serve/%s' % media.blob_key.key()

        image_fetch.append({'name': media.name,
                            'id': media.stuyId,
                            'email': media.email,
                            'event': media.event,
                            'file': media.blob_key.filename,
                            'thumbnail_link': image_link_thumb,
                            'image_link': image_link_full,
                            'key': media.blob_key.key()
                           })
    return image_fetch

# In case Image API cannot handle uploaded file, BlobHandler will serve the file directly
class BlobHandler(blobstore_handlers.BlobstoreDownloadHandler):
    
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

app = webapp2.WSGIApplication([
    ('/admin/serve/([^/]+)?', BlobHandler),
#    ('/admin/approve/([^/]+)?', ApproveHandler),
#    ('/admin/delete/([^/]+)?', DeleteHandler),
    ('/admin.*', AdminPage)
], debug=True)
