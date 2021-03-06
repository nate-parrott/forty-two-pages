import flask, sys
from app import db, memcached
import pymongo
from BeautifulSoup import BeautifulSoup as bs
import os

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
	if is_custom_domain(host):
		site = db.sites.find_one({"custom_domain": host}, sort=[("custom_domain_set_date", pymongo.ASCENDING)])
		return site['name'] if site else None
	else:
		return None

def is_custom_domain(host):
	parts = host.split('.42pag.es')
	return not (len(parts) > 1 and parts[-1] == '')

def log(txt):
	print txt
	sys.stdout.flush()

def html_has_text(html):
	return bs(html).text.strip() != ''

def data_file(name):
	return open(os.path.join(os.path.dirname(__file__), 'data', name), 'r').read()

def cache_it(func, get_key):
	def cache(*args, **kwargs):
		key = get_key(*args, **kwargs)
		cached = memcached.get(key) if key else None
		if cached:
			log("Served %s from cache! (key: %s)"%flask.request.url, key)
			return cached
		else:
			result = func(*args, **kwargs)
			if key:
				memcached.set(key, result)
			return result

def soup_for_fragment_inside_div(fragment, attrs=""):
	return bs("<div %s>"%attrs + fragment + "</div>").div
	
def format_date(dt):
	return "{month} {dt.day}, {dt.year}".format(month=dt.strftime("%B"), dt=dt) 
