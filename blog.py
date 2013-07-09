import os
import re
from string import letters
#from signup import Welcome, SignUp
import webapp2
import jinja2
from prettydate import pretty_date
import json
import urllib

from google.appengine.ext import db
from datetime import datetime

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

	# def render_json(self, d):
	# 	jsontxt = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))
 #        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
 #        self.write(jsontxt)

    def getpost(self, post_id):
    	post = BlogEntries.get_by_id(int(post_id))
    	if not post:
	        self.abort(404)
    	return post




#BLOG

class Blog(BaseHandler):
	def get(self):
		self.render_front()

	def render_front(self, subject = "", content = ""):
		posts = db.GqlQuery('SELECT * FROM BlogEntries ORDER BY created DESC')
		dquery = pretty_date(datetime.now())
		self.render('blog.html', subject = subject, content = content, posts = posts, dquery = dquery)

class BlogJson(BaseHandler):
	"""docstring for BlogJson"""
	def get(self):
		posts = db.GqlQuery('SELECT * FROM BlogEntries ORDER BY created DESC')
		d = []
		for post in posts:
			d = d + [post.as_dict()]
		jsontxt = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		self.write(jsontxt)

#PERMALINK

class Permalink(BaseHandler):
    def get(self, post_id):
    	post = self.getpost(post_id)
    	dquery = pretty_date(datetime.now())
    	self.render('blog-article.html', subject = post.subject, content = post.content, post = post, dquery = dquery)


    	# if urlarg.find('.'):
    	# 	print str(urlarg.find('.'))
    	# 	post_id = urlarg.split('.')[0]
    	# 	print "found"

    	# else:
    	# 	print "else"
    		# self.abort(404)

    	# post = db.GqlQuery.get(key_id)
    	# if post:
    	# 	self.render('blog-article.html', subject = post.subject, content = post.content, post = post, dquery = dquery)

# 		posts = db.GqlQuery('SELECT * FROM BlogEntries ORDER BY created DESC')
# 		if BlogEntries.get_by_id(int(key_id)):
# 			post = BlogEntries.get_by_id(int(key_id))
# 			dquery = pretty_date(datetime.now())
# 			self.render('blog-article.html', subject = post.subject, content = post.content, post = post, dquery = dquery)
# 		else:
# 			self.error(404)
# #			self.redirect('/static/404.html')


class PermaJson(BaseHandler):
	"""
	class inspired by https://github.com/wh5a/cs253/blob/master/blog.py for json page rendering
	"""
	def get(self, post_id):
		post = self.getpost(post_id)
		d = post.as_dict()
		jsontxt = json.dumps(d, sort_keys=False, indent=4, separators=(',', ': '))
		# jsontxt = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))
		self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
		self.write(jsontxt)
		# self.render_json(d)

	# def render_json(self, d):
	# 	jsontxt = json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))
	# 	# print jsontxt
	# 	# self.write("bingo")
	# 	# self.write(jsontxt)
 #        a = self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
 #        self.write(jsontxt)
		
#NEWPOST

class NewPost(BaseHandler):
	def get(self):
		self.render('newpost.html', subject = "", content = "", error="")
	
	def post(self):
		testerr = False
		subject = self.request.get('subject')
		content = self.request.get('content')
		
		if subject == "" or content == "":
			testerr = True
			error = "subject and content, please!"
		else:
			error = ""

		self.render('newpost.html',  subject = subject, content = content, error = error)

		if not testerr:
			b = BlogEntries(subject = subject, content = content)
			b.put()
			self.redirect('/blog/%s' % str(b.key().id()))


class BlogEntries(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)


	def as_dict(self):
		time_fmt = '%c'
		d = {'subject': self.subject,
		'content': self.content,
		'created': self.created.strftime(time_fmt),
		'last_modified': self.last_modified.strftime(time_fmt)
     	}
		return d
		