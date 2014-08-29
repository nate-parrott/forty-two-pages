from app import app, templ8
import flask
import os
import json
import model
import permissions
import util

class Theme(object):
	@staticmethod
	def all():
		themes = []
		themes_dir = os.path.join(os.path.dirname(__file__), 'data', 'themes')
		for name in os.listdir(themes_dir):
			path = os.path.join(themes_dir, name)
			if os.path.isdir(path) and name[0] != '.':
				themes.append(Theme(path))
		return themes
	
	@staticmethod
	def named(name):
		for theme in Theme.all():
			if theme.name.lower() == name.lower():
				return theme
	
	def __init__(self, path):
		self.path = path
		_, self.name = os.path.split(path)
		
	def thumbnail(self):
		return flask.send_file(os.path.join(self.path, 'thumbnail.png'), mimetype='image/png')
	
	def get_theme_content(self):
				return {
					content: 
						open(os.path.join(self.path, content+'.'+content)).read()
						if os.path.exists(os.path.join(self.path, content+'.'+content)) 
						else ''
					for content in ['html', 'css', 'js'] 
					}

@app.route('/__meta/themes')
def theme_list():
	return templ8("themes.html", {"themes": Theme.all()})

YOUR_CONTENT_HERE = util.data_file("yourContentHere.svg")
@app.route('/__meta/yourContentHere.svg')
def svg():
	return flask.Response(YOUR_CONTENT_HERE, mimetype='image/svg+xml')

@app.route('/__meta/theme/thumbnail')
def theme_thumbnail():
	return Theme.named(flask.request.args.get('theme')).thumbnail()

@app.route('/__meta/theme/set_theme', methods=['POST'])
@permissions.protected
def use_theme():
	page = model.Page(model.Site.current(), 'theme')
	theme = Theme.named(flask.request.form.get('theme'))
	content = theme.get_theme_content()
	page.update({"css": content['css'], "js": content['js'], "source": content['html']})
	return flask.redirect('/theme?edit')

