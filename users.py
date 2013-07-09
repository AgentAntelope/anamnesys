import webapp2
import jinja2
from google.appengine.ext import db
from datetime import datetime

class CreateUser(db.Model):
    username = db.StringProperty(required = True)
    uspwsalthash = db.StringProperty(required = True)
    user_id = db.IntegerProperty(required = True)
    email = db.StringProperty(required = True)
    salt = db.StringProperty(required = True)
    dtcreated = db.DateTimeProperty(auto_now_add = True)
