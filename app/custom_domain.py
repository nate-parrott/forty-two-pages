from app import app, db, templ8, limiter
import settings
import model
import flask
import heroku
import util
import permissions

class CustomDomainFormField(settings.FormFieldRecordingSetDate):
	def try_set_str(self, str):
		if heroku.add_domain(str):
			util.log('success')
			return super(CustomDomainFormField, self).try_set_str(str)
		else:
			self.error_msg = "We couldn't register that domain."
			return False

def custom_domain_rate_limit():
	if flask.request.method == 'POST':
		return '10/day;2/minute'
	else:
		return '1/second'

@app.route('/__meta/domain', methods=['GET', 'POST'])
@limiter.limit(custom_domain_rate_limit)
@permissions.protected
def domain():
	site = model.Site.current()
	settings = [
		CustomDomainFormField(model=site, name='custom_domain', label="Your domain:", placeholder="www.example.com", description="This <em>must</em> include the www. or other subdomain, but <em>not</em> http://.")
	]
	
	if flask.request.method == 'POST':
		for s in settings:
			s.set_from_form(flask.request.form)
	
	return templ8("custom_domain.html", {
		"settings": "\n".join([s.html() for s in settings]),
		"site_name": site.record.get('name', '')
	})
