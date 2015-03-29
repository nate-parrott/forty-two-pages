from app import app, db, templ8, limiter
import flask, util, model
import permissions
import themes
import datetime

def get_title(page, site):
	if 'title' in page.record and len(page.record['title']) > 0:
		return page.record['title']
	if page.record['name'] == '':
		return site.record['name']
	else:
		return page.record['name'].split('/')[-1]

def page_limit():
	if 'edit' in flask.request.args:
		return '15/minute;500/hour;1000/day'
	else:
		return '4/second'

def extract_place_in_head_content(code):
	# returns (place_in_head, code)
	place_in_head = ''
	
	start = '<!--PLACE-IN-HEAD-->'
	end = '<!--END-PLACE-IN-HEAD-->'
	if start in code and end in code:
		snip_start = code.index(start)
		snip_end = code.index(end) + len(end)
		if snip_start > snip_end:
			place_in_head = code[snip_start:snip_end]
			code = code[:snip_start] + code[snip_end:]
	return (place_in_head, code)
			
@app.route('/')
@app.route('/<path:name>')
@limiter.limit(page_limit)
def page(name = ""):
	if util.site() == None:
		return flask.redirect('http://42pag.es')
	
	edit = "edit" in flask.request.args
	
	is_theme_editor = name=='theme'
	if is_theme_editor:
		if not edit:
			return flask.redirect('theme?edit')
		theme_list_code = themes.theme_list()
	else:
		theme_list_code = None
		
	site = model.Site.current()
	page = model.Page(site, name, lazy=True)
	
	if site.record.get('locked_forever', False):
		flask.abort(404)
	
	if is_theme_editor:
		theme = None
	else:
		theme = page.theme()
	
	source = page.record.get('source', '')
	css = page.record.get('css', '')
	js = page.record.get('js', '') 
	title = page.record['title']
	
	page_code = page.render(edit, preserve_source=edit)
	place_in_head = ''
	if not edit:
		place_in_head, page_code = extract_place_in_head_content(page_code)
	
	if edit and not permissions.can_acting_user_edit_site(site):
		return flask.redirect("/__meta/noedit")
	
	config_classes = []
	if util.site_name_if_custom_domain() != None:
		config_classes.append("__config_custom_domain")
	if edit:
		config_classes.append("__config_edit_mode")
	if is_theme_editor:
		config_classes.append("__config_theme_page")
	else:
		config_classes.append("__config_not_theme_page")
	
	if 'create' in flask.request.args:
		flask.session['created_sites'] = list(set(flask.session.get('created_sites', []) + [site.record['name']]))
	
	show_edit_hint = False
	show_published_hint = False
	if not edit and name=='' and site.record['name'] in flask.session.get('created_sites', []) and site.record['name'] not in flask.session.get('sites_shown_published_hint_for', []):
		show_published_hint = True
		flask.session['sites_shown_published_hint_for'] = flask.session.get('sites_shown_published_hint_for', []) + [site.record['name']]
	
	markup = templ8("page.html", {
		"title": title, 
		"page_code": page_code,
		"place_in_head": place_in_head,
		"css": css,
		"config_classes": ' '.join(config_classes),
		"edit": edit,
		"locked": len(permissions.emails_for_site(site)) > 0,
		"is_theme_editor": is_theme_editor,
		"theme": theme,
		"theme_list_code": theme_list_code,
		"page_url": flask.request.base_url,
		"page": page,
		"show_edit_hint": show_edit_hint,
		"show_published_hint": show_published_hint,
		"show_debugger": 'd' in flask.request.args and permissions.can_acting_user_edit_site(site)
	})
	return (markup, 200, {"X-XSS-Protection": 0})

@app.route('/__meta/servejs/')
@app.route('/__meta/servejs/<path:name>')
def serve_js(name=''):
	page = model.Page(model.Site.current(), name)
	return page.record.get('js', '')
