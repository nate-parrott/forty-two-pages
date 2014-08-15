import os
from flask import Flask
import pymongo

class Flask42(Flask):
    def get_send_file_max_age(self, name):
		if app.debug:
			return 0
		else:
			return Flask.get_send_file_max_age(self, name)

app = Flask42(__name__)
app.secret_key = "94nY3,R83nf#8qjq02@^ frwfjiwHFEhe028.dfumf2x 0d"
app.config['MAX_CONTENT_LENGTH'] = 512 * 1024 * 1024

# production logging:
import logging
from logging import StreamHandler
file_handler = StreamHandler()
app.logger.setLevel(logging.DEBUG)  # set the desired logging level here
app.logger.addHandler(file_handler)

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('app', 'templates'))
env.autoescape = True
def templ8(name, vars):
	return env.get_template(name).render(vars)

if 'MONGOHQ_URL' in os.environ:
	db = pymongo.MongoClient(os.environ['MONGOHQ_URL']).app28469442
else:
	db = pymongo.MongoClient().fortytwo

import edit
import upload
import settings
import code_edit
import page # imported last, because it has a catch-all URL pattern
