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
		self.record['site'] = model.Site.current().record['name']
		self.record['like_url'] = flask.request.args.get('url', '')
	
	def display_name(self):
		return "An embed"
	
	def settings_fields(self):
		return []
	
	def render(self):
		return ""
	
	def embed_element_attrs(self):
		return ""

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
	if 'site' in embed.record and not permissions.can_acting_user_edit_site(model.Site(embed.record['site'])):
		flask.abort(503)
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
	return "<div data-embed-id='%s' draggable='true' class='%s' %s>%s</div>"%(obj.id(), classes, obj.embed_element_attrs(), innerHTML)

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
		like_url = self.record['like_url']
		return """<iframe src="//www.facebook.com/plugins/like.php?href={URL}&amp;width=136&amp;layout=button_count&amp;action=like&amp;show_faces=true&amp;share=true&amp;height=21&amp;appId=280031018856571" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:136px; height:21px;" allowTransparency="true"></iframe>""".replace("{URL}", urllib.quote_plus(like_url))
CLASSES_FOR_EMBED_TYPES['like'] = LikeButton

class Disqus(Embed):
	def display_name(self): return "Disqus comments"
	def embed_element_attrs(self): return "style='width: 100%'"
	def render(self):
		return """<div id="disqus_thread"></div>
    <script type="text/javascript">
        /* * * CONFIGURATION VARIABLES: EDIT BEFORE PASTING INTO YOUR WEBPAGE * * */
        var disqus_shortname = '42pages'; // required: replace example with your forum shortname

        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
    </script>
    <noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>
    <a href="http://disqus.com" class="dsq-brlink">comments powered by <span class="logo-disqus">Disqus</span></a>
    """
CLASSES_FOR_EMBED_TYPES['disqus'] = Disqus
