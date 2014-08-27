from app import app, db, templ8
import flask, util, model
import permissions
import themes

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
	
	is_theme_editor = name=='/__meta/theme'
	if is_theme_editor:
		if not edit:
			return flask.redirect('/__meta/theme?edit')
		theme_list_code = themes.theme_list()
	else:
		theme_list_code = None
	
		
	site = model.Site.current()
	page = model.Page(site, name, lazy=True)
	
	source = page.record.get('source', '')
	rendered = page.render()
	css = page.record.get('css', '')
	js = page.record.get('js', '') 
	title = page.record['title']
	
	if edit and not permissions.can_acting_user_edit_site(site):
		return flask.redirect("/__meta/noedit")
	
	config_classes = []
	if util.site_name_if_custom_domain() != None:
		config_classes.append("__config_custom_domain")
	
	return templ8("page.html", {
		"title": title, 
		"rendered": rendered,
		"source": source, 
		"css": css, 
		"js": js,
		"config_classes": ' '.join(config_classes),
		"edit": edit,
		"locked": len(permissions.emails_for_site(site)) > 0,
		"is_theme_editor": is_theme_editor,
		"theme_list_code": theme_list_code
	})
