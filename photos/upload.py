from __future__ import with_statement
from photos import JINJA_ENVIRONMENT, Media
from google.appengine.api import files, images
from google.appengine.ext import blobstore, db
from google.appengine.ext.webapp import blobstore_handlers
import json
import re
import urllib
import webapp2

MIN_FILE_SIZE = 1  # bytes
MAX_IMAGE_FILE_SIZE = 10000000  # bytes
MAX_VIDEO_FILE_SIZE = 1000000000 # bytes
IMAGE_TYPES = re.compile('image/(gif|p?jpeg|(x-)?png)')
VIDEO_TYPES = re.compile('mp4|avi')
THUMBNAIL_MODIFICATOR = '=s100'  # max width / height
EXPIRATION_TIME = 300 # cache expiration

def cleanup(blob_keys):
    blobstore.delete(blob_keys)

class UploadHandler(webapp2.RequestHandler):

    def initialize(self, request, response):
        super(UploadHandler, self).initialize(request, response)
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers[
            'Access-Control-Allow-Methods'
        ] = 'OPTIONS, HEAD, GET, POST, PUT, DELETE'
        self.response.headers[
            'Access-Control-Allow-Headers'
        ] = 'Content-Type, Content-Range, Content-Disposition'

    def validate(self, file):
        if file['size'] < MIN_FILE_SIZE:
            file['error'] = 'File is too small.'
        elif file['size'] > MAX_IMAGE_FILE_SIZE and IMAGE_TYPES.match(file['type']):
            file['error'] = 'Image file is too big!'
        elif file['size'] > MAX_VIDEO_FILE_SIZE and VIDEO_TYPES.match(file['type']):
            file['error'] = 'Video file is too big!'
        elif not IMAGE_TYPES.match(file['type']) and not VIDEO_TYPES.match(file['type']):
            file['error'] = 'Filetype not allowed!'
        else:
            return True
        return False

    def get_file_size(self, file):
        file.seek(0, 2)  # Seek to the end of the file
        size = file.tell()  # Get the position of EOF
        file.seek(0)  # Reset the file position to the beginning
        return size

    def write_blob(self, data, info):
        blob = files.blobstore.create(
            mime_type=info['type'],
            _blobinfo_uploaded_filename=info['name']
        )
        with files.open(blob, 'a') as f:
            f.write(data)
        files.finalize(blob)
        return files.blobstore.get_blob_key(blob)

    def handle_upload(self, person, stuyId, email, event):
        results = []
        blob_keys = []
        for name, fieldStorage in self.request.POST.items():
            if type(fieldStorage) is unicode:
                continue
            result = {}
            result['name'] = re.sub(
                r'^.*\\',
                '',
                fieldStorage.filename
            )
            result['type'] = fieldStorage.type
            result['size'] = self.get_file_size(fieldStorage.file)
            if self.validate(result):
                blob_key = str(
                    self.write_blob(fieldStorage.value, result)
                )
                blob_keys.append(blob_key)
                if (IMAGE_TYPES.match(result['type'])):
                    try:
                        result['url'] = images.get_serving_url(
                            blob_key,
                            secure_url=self.request.host_url.startswith(
                                'https'
                            )
                        )
                        result['thumbnailUrl'] = result['url'] +\
                            THUMBNAIL_MODIFICATOR
                    except:  # Could not get an image serving url
                        pass
                if not 'url' in result:
                    result['url'] = self.request.host_url +\
                        '/' + blob_key + '/' + urllib.quote(
                            result['name'].encode('utf-8'), '')
                uploaded = Media(name=person, stuyId=stuyId, email=email, event=event, blob_key=blob_key)
                db.put(uploaded)
            results.append(result)
        return results

    def options(self):
        pass

    def head(self):
        pass

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('upload.html')
        self.response.write(template.render({}))

    def post(self):
        result = {'files': self.handle_upload(self.request.get('person'), self.request.get('id'), self.request.get('email'), self.request.get('event'))}
        s = json.dumps(result, separators=(',', ':'))
        redirect = self.request.get('redirect')
        if redirect:
            return self.redirect(str(
                redirect.replace('%s', urllib.quote(s, ''), 1)
            ))
        if 'application/json' in self.request.headers.get('Accept'):
            self.response.headers['Content-Type'] = 'application/json'
        self.response.write(s)

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, key, filename):
        if not blobstore.get(key):
            self.error(404)
        else:
            # Prevent browsers from MIME-sniffing the content-type:
            self.response.headers['X-Content-Type-Options'] = 'nosniff'
            # Cache for the expiration time:
            self.response.headers['Cache-Control'] = 'public,max-age=%d' % EXPIRATION_TIME
            # Send the file forcing a download dialog:
            self.send_blob(key, save_as=filename, content_type='application/octet-stream')

app = webapp2.WSGIApplication([
    ('/upload', UploadHandler),
    ('/upload([^/]+)/([^/]+)', DownloadHandler)
], debug=True)
