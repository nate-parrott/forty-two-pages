from app import app, db, templ8
import flask, util, model

def get_title(page, site):
	if 'title' in page.record and len(page.record['title']) > 0:
		return page.record['title']
	if page.record['name'] == '':
		return site.record['name']
	else:
		return page.record['name'].split('/')[-1]

@app.route('/')
@app.route('/<path:name>')
def page(name = ""):
	if util.site() == None:
		return "index!"
	site = model.Site.current()
	page = model.Page(site, name)
	rendered = page.render()
	css = page.record.get('css', '')
	js = page.record.get('js', '')
	title = page.record['title']
	
	config_classes = []
	if util.site_name_if_custom_domain() != None:
		config_classes.append("__config_custom_domain")
	
	return templ8("page.html", {
		"title": title, 
		"rendered": rendered, 
		"css": css, 
		"js": js,
		"config_classes": ' '.join(config_classes)
	})
