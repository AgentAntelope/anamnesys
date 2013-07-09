import webapp2
import string

from string import letters
from anamnesis import Anamnesis
from base import BaseHandler

class Home(BaseHandler):
  def get(self):
    self.render('home.html')

app = webapp2.WSGIApplication([
                               ('/', Home),
                               ('/anamnesis', Anamnesis),
                               ],
                              debug=True)
