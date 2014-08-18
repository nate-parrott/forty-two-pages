import flask, sys
from app import db
import pymongo
from BeautifulSoup import BeautifulSoup as bs

def site():
	name_for_custom_domain = site_name_if_custom_domain()
	if name_for_custom_domain: 
		return name_for_custom_domain
	
	subdomain = flask.request.host.split(".")[0]
	if subdomain in ['192', 'localhost', 'www', 'nip', '127']:
		return None
	return subdomain

def site_name_if_custom_domain():
	host = flask.request.host
	site = db.sites.find_one({"custom_domain": host}, sort=[("custom_domain_set_date", pymongo.ASCENDING)])
	return site['name'] if site else ''

def log(txt):
	print txt
	sys.stdout.flush()

def html_has_text(html):
	return bs(html).text.strip() != ''
