from app import app, db, templ8
import flask, util, model
import permissions

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
		return "index!"
		
	site = model.Site.current()
	page = model.Page(site, name)
	
	source = page.record.get('source', '')
	rendered = page.render()
	css = page.record.get('css', '')
	js = page.record.get('js', '') 
	title = page.record['title']
	edit = "edit" in flask.request.args
	
	if edit and not permissions.can_acting_user_edit_site(site):
		return flask.redirect("/__meta/noedit")
	
	header = None
	if page.record.get('include_header', False) and name != '__meta/header':
		header_model = site.header()
		if header_model and util.html_has_text(header_model.record.get('source', '')):
			header = {
				"rendered": header_model.render(),
				"css": header_model.record.get('css', ''),
				"js": header_model.record.get('js', '')
			}
	
	config_classes = []
	if util.site_name_if_custom_domain() != None:
		config_classes.append("__config_custom_domain")
	
	is_header = name == '__meta/header'
	if is_header:
		config_classes.append("__config_viewing_header")
		css = model.DEFAULT_CSS
	
	if header == None and not is_header:
		config_classes.append("__config_no_header")
	
	return templ8("page.html", {
		"title": title, 
		"rendered": rendered,
		"source": source, 
		"css": css, 
		"js": js,
		"config_classes": ' '.join(config_classes),
		"edit": edit,
		"header": header,
		"is_header": is_header,
		"locked": len(permissions.emails_for_site(site)) > 0
	})
