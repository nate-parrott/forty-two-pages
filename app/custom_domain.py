from app import app, db, templ8
import settings
import model
import flask
import heroku
import util

class CustomDomainFormField(settings.FormFieldRecordingSetDate):
	def try_set_str(self, str):
		if heroku.add_domain(str):
			util.log('success')
			return super(CustomDomainFormField, self).try_set_str(str)
		else:
			self.error_msg = "We couldn't register that domain."
			return False

@app.route('/__meta/domain', methods=['GET', 'POST'])
def domain():
	site = model.Site.current()
	settings = [
		CustomDomainFormField(model=site, name='custom_domain', label="Your domain:", placeholder="example.com")
	]
	
	if flask.request.method == 'POST':
		for s in settings:
			s.set_from_form(flask.request.form)
	
	return templ8("custom_domain.html", {
		"settings": "\n".join([s.html() for s in settings]),
		"site_name": site.record.get('name', '')
	})
