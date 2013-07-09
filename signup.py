import webapp2
import re
from blog import BaseHandler
import os
import jinja2
from users import CreateUser
import random
from google.appengine.ext import db
import hashlib
import string

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)  

class SignUp(BaseHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        params = dict(username = username,
                      email = email)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if used_username(username):
            params['error_username_used'] = "That user already exists."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            user_id = createuserid()
            salt = make_salt()
            hashthemall = hashuserpwsalt(username, password, salt)
            a = CreateUser(username = username, user_id = user_id, uspwsalthash = hashthemall, email = email, salt = salt)
            a.put()

            #make it a str 
            cookie_val = str(user_id) + '|' + str(hashthemall)
            self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % cookie_val)
            self.redirect('/welcome')

def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def hashuserpwsalt(username, password, salt):
    hs = hashlib.sha256(username + password + salt).hexdigest()
    return hs

def used_username(username):
    accounts = db.GqlQuery("SELECT * FROM CreateUser WHERE username = :usern", usern = username)
    for account in accounts:
        if account.username == username:
            return True
    return False

def createuserid():
    possid = random.randint(1000, 9999)
    ids = db.GqlQuery("SELECT * FROM CreateUser")    
    for e in ids:
        if possid == e.user_id:
            return createuserid()
    return possid

class Welcome(BaseHandler):
    def get(self):
        cookie_val = self.request.cookies.get('user_id')
        if len(str(cookie_val)) > 10:
            cook_split = str(cookie_val).split('|')
            user_id = cook_split[0]
            hashthemall = cook_split[1]
            hashmem = "_"
            username = "bug"

            accounts = db.GqlQuery("SELECT * FROM CreateUser WHERE user_id = %s" % user_id)
            for account in accounts:
                username = account.username
                hashmem = account.uspwsalthash
            
            if hashmem == hashthemall:
                self.render('welcome.html', username = username)
            else:
                self.redirect('/signup')

        else:
            self.redirect('/signup')

class Login(BaseHandler):
    def get(self):
        cookie_val = self.request.cookies.get('user_id')
        self.render('login.html')

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')

        params = dict(username = username)

        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True

        if not validation_user_pw(username,password):
            params['err_userpw'] = "Nope, Invalid username or password!"
            have_error = True

        if have_error:
            self.render('login.html', **params)
        else:
            find_user_id(username, password)
            cookie_val = str(user_id) + '|' + str(hashthemall)
            self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % cookie_val)
            self.redirect('/welcome')

def find_user_id(username, password):
#si username et password return account.user_id, account.uspwsalthash
    accounts = db.GqlQuery("SELECT * FROM CreateUser WHERE username = :usern", usern = username)
    for account in accounts:
        if hashuserpwsalt(account.username, password, account.salt) == account.uspwsalthash:
            global user_id, hashthemall
            user_id, hashthemall = account.user_id, account.uspwsalthash
            return
        else:
            self.redirect('/signup')

class Logout(BaseHandler):
    def get(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.redirect('/signup')


def validation_user_pw(username,password):
    accounts = db.GqlQuery("SELECT * FROM CreateUser WHERE username = :usern", usern = username)
    for account in accounts:
        if hashuserpwsalt(account.username, password, account.salt) == account.uspwsalthash:
            return True
        else:
            return False