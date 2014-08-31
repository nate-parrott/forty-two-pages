from app import app, db, templ8
import model
import permissions
import util
import flask
import urllib
import settings
from bson.objectid import ObjectId

class Embed(model.MongoObject):
	collection = db.embeds
	def __init__(self, record=None):
		if record:
			self.record = record
		else:
			self.create_record()
	
	@classmethod
	def WithId(self, id):
		record = self.collection.find_one({"_id": ObjectId(id)})
		return globals()[record['class']](record)

	def initialize_record(self):
		super(Embed, self).initialize_record()
		self.record['class'] = self.__class__.__name__
	
	def display_name(self):
		return "An embed"
	
	def settings_fields(self):
		return []
	
	def render(self):
		return ""
	
	"""def placeholder_size(self):
		return (100, 100)
	
	def render_placeholder(self):
		w,h = self.placeholder_size()
		classes = ['__embed']
		if len(self.settings_fields()) > 0:
			classes.append('__editable_embed')
		return "<img data-embed-id='%s' class='%s' src='/__meta/embed/%s/placeholder.svg' style='width: %f; height: %f'/>"%(self.id(), ' '.join(classes), self.id(), w, h)"""

@app.route('/__meta/embed/<id>/placeholder.svg')
def placeholder(id):
	embed = Embed.WithId(id)
	w, h = embed.placeholder_size()
	text = templ8("embedPlaceholderImage.svg", {
		"name": embed.display_name(),
		"width": w,
		"height": h
	})
	return flask.Response(text, mimetype='image/svg+xml')

@app.route('/__meta/embed/<id>/edit', methods=['GET', 'POST'])
@permissions.protected
def edit(id):
	embed = Embed.WithId(id)
	settings = embed.settings_fields()
	if flask.request.method == 'POST':
		for field in settings:
			field.set_from_form(flask.request.form)
	settings_html = '\n'.join(map(lambda x: x.html(), settings))
	return templ8("embed_settings.html", {
		"name": embed.display_name(),
		"settings_html": settings_html,
		"id": id,
		"embed_content": embed.render()
	})

@app.route('/__meta/embed')
def embed_list():
	return templ8("embed_list.html", {})

@app.route('/__meta/embed/create', methods=['POST'])
def create_embed():
	type = flask.request.args.get('type')
	obj = CLASSES_FOR_EMBED_TYPES[type]()
	innerHTML = obj.render()
	classes = []
	if len(obj.settings_fields()) > 0:
		classes.append("__editable_embed")
	return "<div data-embed-id='%s' draggable='true' class='%s'>%s</div>"%(obj.id(), classes, innerHTML)

CLASSES_FOR_EMBED_TYPES = {}

class Example(Embed):
	def display_name(self): return "Example"
	def initialize_record(self):
		super(Example, self).initialize_record()
		self.record['text'] = 'abcdef'
	def settings_fields(self):
		return [settings.FormField(self, "text", label="Text")]
	def render(self):
		return "<h1 style='text-shadow: 0px 0px 3px purple'>%s</h1>"%self.record['text']
CLASSES_FOR_EMBED_TYPES['example'] = Example

class LikeButton(Embed):
	def display_name(self): return "Like button"
	def render(self):
		like_url = flask.request.args.get('url', '')
		return """<iframe src="//www.facebook.com/plugins/like.php?href={URL}&amp;width=136&amp;layout=button_count&amp;action=like&amp;show_faces=true&amp;share=true&amp;height=21&amp;appId=280031018856571" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:136px; height:21px;" allowTransparency="true"></iframe>""".replace("{URL}", urllib.quote_plus(like_url))
	def placeholder_size(self):
		return (136,21)
CLASSES_FOR_EMBED_TYPES['like'] = LikeButton
