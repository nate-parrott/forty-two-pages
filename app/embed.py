from app import app, db, templ8
import model
import permissions
import util
import flask

class Embed(model.MongoObject):
	def __init__(self, id=None):
		if id:
			self.load_record({"_id": id})
		else:
			self.create_record()
	
	collection = db.embeds
	def initialize_record(self):
		pass
	
	def display_name(self):
		return "An embed"
	
	def size(self):
		return (100, 100)
	
	def settings_fields(self):
		return []
	
	def render(self):
		return ""


@app.route('/__meta/embed/:id/placeholder.svg')
def placeholder(id):
	embed = Embed(id)
	w, h = embed.size()
	return templ8("embedPlaceholderImage.svg", {
		"embed": embed.display_name(),
		"width": width,
		"height": height
	})

@app.route('/__meta/embed/:id/edit', methods=['GET', 'POST'])
def edit(id):
	embed = Embed(id)
	settings = embed.settings_fields()
	if flask.request.method == 'POST':
		for field in settings:
			field.set_from_form(flask.request.form)
	settings_html = '\n'.join(map(lambda x: x.html(), settings))
	return templ8("embedSettings.html", {
		"name": embed.display_name(),
		"settings_html": settings_html
	})



class LikeButton(Embed):
	def display_name(self): return "Like button"
	def render(self):
		like_url = flask.request.url
		return """<div id="fb-root"></div>
<script>(function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&appId=280031018856571&version=v2.0";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script><div class="fb-like" data-href="{URL}" data-layout="button_count" data-action="like" data-show-faces="true" data-share="false"></div>""".replace("{URL}", flask.url_for(''))
