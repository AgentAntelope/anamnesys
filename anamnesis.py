from datetime import datetime, timedelta
from base import BaseHandler
from google.appengine.ext import db
from signup import SignUp, Login

class Anamnesis(BaseHandler):
	"""Anamnesis open your past bookmarks and allow you to discuss between your past you, your present and your future you. Possible effects include extended memory and possibly schizophrenia"""
	def get(self):
		listmnems = db.GqlQuery('SELECT * FROM Mnems ORDER BY nexttime ASC')
		now = datetime.now()
		
		#Select urls to display
		listmnemstodisplay = db.GqlQuery('SELECT * FROM Mnems ORDER BY nexttime ASC').fetch(limit=1)
		urlstodisplay = []
		# counter = 0
		for e in listmnemstodisplay:
			if now < e.nexttime : #TEST POUR TEST (TU PEUX PAS)
			# if now > e.nexttime : #TEST NORMAL
				urlstodisplay.append(e.url)
				e.persistence += 1
				e.nexttime = now + timedelta(hours=e.timerint)
				e.put()
			else:
				break

		self.render('anamnesis-home.html', listmnems = listmnems, now = now, urlstodisplay = urlstodisplay)

	def post(self):

		#NEW MNEM
		testerr = False
		error = ""
		congrats = ""
		timer = ""
		url = self.request.get('url')
		
		timequantity = self.request.get('timequantity')
		timequantityint = int(timequantity)
		timeunit = self.request.get('timeunit')
		if timeunit == "hours":
			timeunitint = 1
		elif timeunit == "days":
			timeunitint = 24
		elif timeunit == "months":
			timeunitint = 720
		else:
			testerr = True
			error = "oops, problem with the timer ><!"

		if url == "":
			testerr = True
			error = "url please!"

		if not testerr:
			#convert in hours
			timer = timequantity + ' ' + timeunit
			timerint = timequantityint * timeunitint
			# determine the next date
			nexttime = datetime.now() + timedelta(hours=timerint)
			m = Mnems(url = url, timer = timer, timerint = timerint, nexttime = nexttime, persistence = 0, tobedisplayed = True)
			m.put()
			self.redirect('/anamnesis')
			congrats = "Got it!"

		listmnems = db.GqlQuery('SELECT * FROM Mnems ORDER BY dtcreated DESC')
		self.render('anamnesis-home.html', url = url, timer = timer, error = error, congrats = congrats, listmnems = listmnems)

class Mnems(db.Model):
	url = db.StringProperty(required = True)
	# timequantity = db.IntegerProperty(required = True)
	# timeunit = db.StringProperty(required = True)
	timer = db.StringProperty(required = True)
	timerint = db.IntegerProperty(required = True)
	# category = db.StringProperty(required = False)
	nexttime = db.DateTimeProperty(required = True)
	dtcreated = db.DateTimeProperty(auto_now_add = True)
	dtmodif = db.DateTimeProperty(auto_now = True)
	persistence = db.IntegerProperty(required = True)