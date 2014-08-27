from app import app, templ8
import flask
import os
import json

class Theme(object):
	@staticmethod
	def all():
		themes = []
		themes_dir = os.path.join(os.path.dirname(__file__), 'data', 'themes')
		for name in os.listdir():
			path = os.path.join(themes_dir, name)
			if os.path.isdir(path) and name[0] != '.':
				themes.append(Theme(path))
	
	@staticmethod
	def named(name):
		for theme in Themes.all():
			if theme.name.lower() == name.lower():
				return theme
	
	def __init__(self, path):
		self.path = path
		_, self.name = os.path.split(path)
		
	def thumbnail_data(self):
		return open(os.path.join(self.path, 'thumbnail.png')).read()
	
	def get_template_code(self):
				return json.dumps({
					content: open(os.path.join(self.path, content+'.'+content)) 
					for content in ['html', 'css', 'js'] 
					if os.path.exists(os.path.join(self.path, content+'.'+content))})

@app.route('/__meta/themes')
def theme_list():
	return templ8("themes.html", {"themes": Theme.all()})

@app.route('/__meta/theme/<name>/thumbnail')
def theme_thumbnail(name):
	return flask.Response(Theme.named(name).thumbnail_data, mimetype='image/png')

@app.route('/__meta/theme/<name>/code')
def theme_code(name):
	return Theme.named(name).get_template_code()
