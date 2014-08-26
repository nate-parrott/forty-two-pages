from app import app, db, templ8
import flask
import model
import re
import postmark
import hashlib
import os
import base64
import json

# use this as a decorator to mark endpoints as requiring that the acting user has edit permision:
def protected(func):
	def require_write_permissions(*args, **kwargs):
		if can_acting_user_edit_site(model.Site.current()):
			return func(*args, **kwargs)
		else:
			abort(403)

def can_acting_user_edit_site(site):
	emails = emails_for_site(site)
	if len(emails) == 0:
		return True
	else:
		return site.record['name'] in flask.session.get('sites', [])

@app.route('/__meta/can_user_edit_site')
def can_user_edit_site():
	site_name = flask.request.args['site']
	can_edit = (not model.Site.exists(site_name)) or can_acting_user_edit_site(model.Site(site_name))
	return json.dumps({"can_edit": can_edit})

def give_acting_user_permissions_for_site(site):
	flask.session['sites'] = list(set(flask.session.get('sites', []) + [site.record['name']]))

def emails_for_site(site):
	emails = re.split(r"[, ]+", site.record.get('emails_that_can_edit', ''))
	emails = [e for e in emails if len(e) > 1]
	return emails

def mask_email_address(address):
	def mask(s):
		split_point = len(s) - len(s)/2
		return s[:split_point] + '*'*len(s[split_point:])
	if '@' in address:
		name, host = address.split('@', 1)
		return mask(name)+'@'+mask(host)
	else:
		return mask(address)

SALT = "6QR7jxKjKaXkZtrBiHGlHg5Ft1lf0iFu7ul7kX+5SqSEG+DooAh8Snr9DyAamhPrk7OyfxB6eu9d\nXM6sYqmU7jIDJ0DoSYxPHvGUStYftU9MqNVbRDbScM5KdAygyuhfd0Kk6GepZ+savN9rV8P4q8x5\nUFRB9H2hhaWzsIik8hk"

def generate_access_key(site, email):
	# access keys are salted concatenations of the email address and site name:
	return base64.b32encode(hashlib.sha256("%s,%s,%s"%(str(site.record['_id']), email, SALT)).digest())

MASTER_KEY_EMAIL = "y89n3ycf34yf437xtfy9wx7" # special email address used for generating access keys for emails not on the list. NON-REVOKABLE (TODO: change often)

def generate_access_url(site, email):
	return "http://%s.42pag.es/__meta/login/%s"%(site.record['name'], generate_access_key(site, email))

def validate_access_key(key, site):
	for email in emails_for_site(site) + [MASTER_KEY_EMAIL]:
		if generate_access_key(site, email) == key:
			return True
	return False

@app.route('/__meta/noedit', methods=["GET", "POST"])
def noedit():
	site = model.Site.current()
	owners = emails_for_site(site)
	if flask.request.method == 'GET':
		emails = map(mask_email_address, owners)
		return templ8('noedit.html', {"site_name": site.record['name'], "emails": emails})
	else:
		# email a login key to the owner:
		email = [owner for owner in owners if mask_email_address(owner) == flask.request.form['email']][0]
		key = generate_access_key(site, email)
		body = templ8("access_email.html", {"site_name": site.record['name'], "key": key})
		if 'POSTMARK_API_KEY' in os.environ:
			msg = postmark.PMMail(
					api_key = os.environ['POSTMARK_API_KEY'],
					subject = "Edit '%s' on 42Pages"%site.record['name'],
					to = email,
					sender = "robot@42pag.es",
					html_body = body)
			msg.send()
		else:
			print owners
			print body
		return templ8('message.html', {"message": "An email was sent. Click the link in the email to get editing."})

@app.route('/__meta/login/<key>')
def login(key):
	site = model.Site.current()
	if validate_access_key(key, site):
		give_acting_user_permissions_for_site(site)
		return flask.redirect('/')
	else:
		flask.abort(403)
