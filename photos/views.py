from photos import JINJA_ENVIRONMENT
import webapp2

class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

class AdminPage(webapp2.RequestHandler):
    
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('admin.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([
    ('/admin', AdminPage),
    ('/.*', MainPage)
], debug=True)
