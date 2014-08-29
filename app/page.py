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

def cache_key_for_page_request(name = ""):
	if 'edit' in flask.request.args:
		return None
	site = util.site()
	return "page "+name+" on "+name

#@util.cache_it(cache_key_for_page_request) # don't use, doesn't handle invalidation
@app.route('/')
@app.route('/<path:name>')
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
	
	if is_theme_editor:
		theme = None
	else:
		theme = page.theme().record
	
	source = page.record.get('source', '')
	css = page.record.get('css', '')
	js = page.record.get('js', '') 
	title = page.record['title']
	
	page_code = page.render(edit, preserve_source=edit)
	
	if edit and not permissions.can_acting_user_edit_site(site):
		return flask.redirect("/__meta/noedit")
	
	config_classes = []
	if util.site_name_if_custom_domain() != None:
		config_classes.append("__config_custom_domain")
	if edit:
		config_classes.append("__config_edit_mode")
	if is_theme_editor:
		config_classes.append("__config_theme_page")
	
	if 'create' in flask.request.args:
		util.log("CREATE")
		flask.session['created_sites'] = list(set(flask.session.get('created_sites', []) + [site.record['name']]))
	
	show_edit_hint = False
	show_published_hint = False
	if not edit and name=='' and site.record['name'] in flask.session.get('created_sites', []) and site.record['name'] not in flask.session.get('sites_shown_published_hint_for', []):
		util.log("HINT")
		show_published_hint = True
		flask.session['sites_shown_published_hint_for'] = flask.session.get('sites_shown_published_hint_for', []) + [site.record['name']]
	
	return templ8("page.html", {
		"title": title, 
		"page_code": page_code,
		"css": css,
		"js": js,
		"config_classes": ' '.join(config_classes),
		"edit": edit,
		"locked": len(permissions.emails_for_site(site)) > 0,
		"is_theme_editor": is_theme_editor,
		"theme": theme,
		"theme_list_code": theme_list_code,
		"page_url": flask.request.base_url,
		"show_edit_hint": show_edit_hint,
		"show_published_hint": show_published_hint
	})
