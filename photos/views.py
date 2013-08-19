import os, webapp2, jinja2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'])

class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

class UploadForm(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('upload.html')
        self.response.write(template.render({}))

    def post(self):
        template = JINJA_ENVIRONMENT.get_template('upload.html')
        self.response.write(template.render(template_values))

class AdminPage(webapp2.RequestHandler):
    
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))

application = webapp2.WSGIApplication([
    ('/upload', UploadForm),
    ('/admin', AdminPage),
    ('/.*', MainPage)
], debug=True)
