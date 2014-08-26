import os

# new relic:
import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

# flask:
from flask import Flask
class Flask42(Flask):
    def get_send_file_max_age(self, name):
		if app.debug:
			return 0
		else:
			return Flask.get_send_file_max_age(self, name)
app = Flask42(__name__)
app.secret_key = "94nY3,R83nf#8qjq02@^ frwfjiwHFEhe028.dfumf2x 0d"
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# production logging:
import logging
from logging import StreamHandler
file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)
app.logger.addHandler(file_handler)

# templating:
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('app', 'templates'))
env.autoescape = True
def templ8(name, vars):
	return env.get_template(name).render(vars)

# mongodb:
import pymongo
if 'MONGOHQ_URL' in os.environ:
	db = pymongo.MongoClient(os.environ['MONGOHQ_URL']).app28469442
else:
	db = pymongo.MongoClient().fortytwo
db.sites.ensure_index("name", background=True)
db.pages.ensure_index("name", background=True)

# memcached:
import bmemcached
if 'MEMCACHIER_SERVERS' in os.environ:
	mc_servers = os.environ['MEMCACHIER_SERVERS'].split(',')
	mc_username = os.environ['MEMCACHIER_USERNAME']
	mc_password = os.environ['MEMCACHIER_PASSWORD']
else:
	mc_servers = ['mc5.dev.ec2.memcachier.com:11211']
	mc_username = 'fccd85'
	mc_password = 'd30cef12a0'
memcached = bmemcached.Client(mc_servers, mc_username, mc_password)

# import pages:
import edit
import upload
import settings
import code_edit
import custom_domain
import index
import moderate
import page # imported last, because it has a catch-all URL pattern
