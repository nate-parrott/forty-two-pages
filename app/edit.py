from app import app, db, templ8
import model
import flask
import util
import permissions
from beautiful_print import beautiful_print

@app.route('/toolbar')
def toolbar():
	if permissions.can_acting_user_edit_site(model.Site.current()):
		return templ8('toolbar.html', {})
	else:
		# return a javascript redirect:
		return "<script> location = '/__meta/noedit' </script>"

@app.route('/__meta/save/', methods=['POST'])
@app.route('/__meta/save/<path:name>', methods=['POST'])
@permissions.protected
def save_source(name=''):
	source = flask.request.form['source']
	source = beautiful_print(source)
	page = model.Page(model.Site.current(), name)
	page.update({"source": source})
	return "ok"

