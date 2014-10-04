from app import app, db, templ8
import model
import permissions
import util
import flask
import urllib
import settings
from bson.objectid import ObjectId

def refresh_embeds(soup):
	for tag in soup.findAll(attrs={'data-embed-id': True}):
		embed = Embed.WithId(tag['data-embed-id'])
		if embed:
			replacement = util.soup_for_fragment_inside_div(embed.get_rendered_and_wrapped_html()).div
			tag.replaceWith(replacement)

class Embed(model.MongoObject):
	collection = db.embeds
	def __init__(self, record=None):
		if record:
			self.record = record
		else:
			self.create_record()
	
	@classmethod
	def WithId(self, id):
		record = self.collection.find_one({"_id": ObjectId(id), "site": model.Site.current().record['name']})
		return globals()[record['class']](record) if record else None

	def initialize_record(self):
		super(Embed, self).initialize_record()
		self.record['class'] = self.__class__.__name__
		self.record['site'] = model.Site.current().record['name']
	
	def display_name(self):
		return "An embed"
	
	def settings_fields(self):
		return []
	
	def render(self):
		return ""
	
	def embed_element_attrs(self):
		return ""
	
	def embed_type(self):
		for type_name, class_obj in CLASSES_FOR_EMBED_TYPES.iteritems():
			if isinstance(self, class_obj):
				return type_name
	
	def classes(self):
		c = ['__dim_on_hover_embed']
		if len(self.settings_fields()) > 0:
			c.append('__editable_embed')
		return c
	
	def get_rendered_and_wrapped_html(self):
		innerHTML = self.render()
		classes = self.classes()
		return "<div data-embed-id='%s' data-embed-type='%s' draggable='true' class='%s' %s>%s</div>"%(self.id(), self.embed_type(), ' '.join(classes), self.embed_element_attrs(), innerHTML)

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

def create_embed(type):
	obj = CLASSES_FOR_EMBED_TYPES[type]()
	return obj

@app.route('/__meta/embed/create', methods=['POST'])
def create_embed_endpoint():
	type = flask.request.args.get('type')
	return create_embed(type).get_rendered_and_wrapped_html()

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
		like_url = flask.request.url
		return """<iframe src="//www.facebook.com/plugins/like.php?href={URL}&amp;width=136&amp;layout=button_count&amp;action=like&amp;show_faces=true&amp;share=true&amp;height=21&amp;appId=280031018856571" scrolling="no" frameborder="0" style="border:none; overflow:hidden; width:136px; height:21px" allowTransparency="true"></iframe>""".replace("{URL}", urllib.quote_plus(like_url))
CLASSES_FOR_EMBED_TYPES['like'] = LikeButton

class Disqus(Embed):
	def display_name(self): return "Disqus comments"
	def embed_element_attrs(self): return "style='width: 100%'"
	def render(self):
		return """<div id="disqus_thread"></div>
    <script type="text/javascript">
        var disqus_shortname = '42pages';

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

class Map(Embed):
	def display_name(self): return "Map"
	def embed_element_attrs(self): return "style='width: 100%'"
	def initialize_record(self):
		super(Map, self).initialize_record()
		self.record['search'] = "Eiffel Tower, Paris, France"
	def settings_fields(self):
		return [settings.FormField(self, 
			"search", 
			label="Place to show", 
			placeholder="123 Main Street, Tulsa, Oklahoma, United States",
			description="Enter a full address, the name of a city, town or country, or even a search, like \"restaurants near the IFC Center, New York, USA.\"")]
	def render(self):
		return """
		<iframe width="100%" height="450" frameborder="0" style="border:0"
		src="https://www.google.com/maps/embed/v1/search?q={{query}}&key=AIzaSyBeW-B0p38d7tJ5Pdx4u703uFKQep9MARc"></iframe>
		""" .replace('{{query}}', urllib.quote_plus(self.record['search']))
CLASSES_FOR_EMBED_TYPES['map'] = Map


class PageList(Embed):
	def display_name(self): return "Recently Created Pages List"
	def initialize_record(self):
		super(PageList, self).initialize_record()
		self.record['count'] = 10
	def settings_fields(self):
				return [settings.FormField(self,
				"count", 			
				label="Numbers of pages to show", 			
				description="We'll list this number of the most recently created pages on your site. Leave this blank to list every post.")]
	def render(self):
		site = model.Site.current()
		kwargs = {}
		try:
			kwargs['limit'] = int(self.record['count'])
		except Exception:
			pass
		pages = db.pages.find({"site": site.record['name']}, sort=[("created", -1)], **kwargs)
		pages = [p for p in pages if p['name'] not in model.special_pages]
		for p in pages:
			p['formatted_date'] = util.format_date(p['created']) if 'created' in p else ""
		is_authorized_user = permissions.can_acting_user_edit_site(site)
		return templ8("page_list.html", 
		{
			"pages": pages,
			"show_all_link": 'limit' in kwargs,
			"is_authorized_user": is_authorized_user
		})
CLASSES_FOR_EMBED_TYPES['page_list'] = PageList

