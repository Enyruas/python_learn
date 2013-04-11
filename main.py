import webapp2
import jinja2
import os

from google.appengine.api import users
from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])
	
def guestbook_key(guestbook_name='default_guestbook'):
    return ndb.Key('Guestbook', guestbook_name)
	
class GuestWords(ndb.Model):
	author = ndb.UserProperty()
	content = ndb.StringProperty(indexed = False)
	date = ndb.DateTimeProperty(auto_now_add = True)
	
class MainPage(webapp2.RequestHandler):
    def get(self):
        greetings_query = GuestWords.query(ancestor=guestbook_key()).order(-GuestWords.date)
        guest_words = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(greetings=guest_words,
                                                url=url,
                                                url_linktext=url_linktext))

class Login(webapp2.RequestHandler):
    def post(self):
        greeting = GuestWords(parent=guestbook_key())

        if users.get_current_user():
            greeting.author = users.get_current_user()

        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/sign', Login),
], debug=True)