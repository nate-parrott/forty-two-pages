from app import app, templ8
import flask
from permissions import protected
import model
import json

@protected
@app.route('/__meta/code', methods=['GET', 'POST'])
def code_edit():
	site = model.Site.current()
	site_name = site.record['name']
	page_name = flask.request.args.get("page")
	page = model.Page(site, page_name)
	if flask.request.method == 'GET':
		source = page.record.get('source', '')
		css = page.record.get('css', '')
		js = page.record.get('js', '')
		return templ8("code_edit.html", {"source": source, "css": css, "js": js, "page_name": page_name, "site_name": site_name})
	elif flask.request.method == 'POST':
		form = flask.request.form
		page.update({"source": form['source'], "css": form['css'], "js": form['js']})
		return json.dumps({"success": True})

@app.route('/__meta/blank')
def blank():
	return ""
