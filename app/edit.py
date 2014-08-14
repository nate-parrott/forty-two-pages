from app import app, db, templ8
import model
import flask
import util
import permissions

@app.route('/toolbar')
def toolbar():
	if permissions.can_acting_user_edit_site(model.Site.current()):
		return templ8('toolbar.html', {})
	else:
		# return a javascript redirect:
		return "<script> location = '/__meta/noedit' </script>"

@app.route('/__meta/save/', methods=['POST'])
@app.route('/__meta/save/<path:name>', methods=['POST'])
def save_source(name=''):
	source = flask.request.form['source']
	page = model.Page(model.Site.current(), name)
	page.update({"source": source})
	return "ok"

@permissions.protected
@app.route('/__meta/source/')
@app.route('/__meta/source/<path:name>')
def get_source(name=''):
	return model.Page(model.Site.current(), name).record['source']
