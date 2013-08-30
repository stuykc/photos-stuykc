from photos import JINJA_ENVIRONMENT
import webapp2

class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render({}))

app = webapp2.WSGIApplication([
    ('/.*', MainPage)
], debug=True)
