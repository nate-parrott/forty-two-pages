from app import app, db, templ8
from flask import request
import model
import datetime
import permissions

class FormField(object):
	def __init__(self, model, name, label=None, placeholder="", description=None, type="text"):
		self.model = model
		self.name = name
		self.label = label if label else name
		self.placeholder = placeholder
		self.description = description
		self.error_msg = None
		self.type = type
		self.template_name = "form_fields/default.html"
	
	def get_str(self):
		return unicode(self.model.record.get(self.name, ''))
	
	def set_from_form(self, form):
		if self.name in form:
			return self.try_set_str(form[self.name])
		else:
			return False
	
	def try_set_str(self, str_content):
		self.model.update({self.name: str_content})
		return True
	
	def template_keys(self):
		return {
			"name": self.name, 
			"value": self.get_str(), 
			"type": self.type,
			"label": self.label,
			"placeholder": self.placeholder,
			"description": self.description,
			"error": self.error_msg
		}
	
	def html(self):
		return templ8(self.template_name, self.template_keys())

class BooleanFormField(FormField):
	def set_from_form(self, form):
		self.model.update({self.name: (self.name in form)})
		return templ8(self.template_name, {
			"name": self.name, 
			"value": self.get_str(), 
			"type": self.type,
			"label": self.label,
			"placeholder": self.placeholder,
			"description": self.description,
			"error": self.error_msg
		})
	
	def template_keys(self):
		d = super(BooleanFormField, self).template_keys()
		d['checked'] = self.model.record.get(self.name, False)
		return d
	
	def html(self):
		self.template_name = "form_fields/boolean.html"
		return super(BooleanFormField, self).html()

class FormFieldRecordingSetDate(FormField):
        def try_set_str(self, str_content):
                self.model.update({self.name: str_content, self.name+'_set_date': datetime.datetime.now()})
                return True

@permissions.protected
@app.route('/__meta/settings', methods=['GET', 'POST'])
def settings():
	page_name = request.args.get('page')
	site = model.Site.current()
	page = model.Page(site, page_name)
	
	site_fields = [
		FormField(site, "emails_that_can_edit", 
			label="Emails that can edit this site", 
			placeholder="sam@gmail.com, casey@yahoo.com",
			description="When this is empty, anyone can edit this site. If you add a list of emails, separated by commas, only they will be allowed to edit.")
	]
	
	page_fields = [
		FormField(page, "title", "Title"),
	]
	
	if request.method == 'POST':
		permissions.give_acting_user_permissions_for_site(site) # in case the user modifies settings and locks themselves out
		for field in site_fields + page_fields:
			field.set_from_form(request.form)
	
	return templ8("settings.html", {
		"site_fields": '\n'.join([_.html() for _ in site_fields]),
		"page_fields": '\n'.join([_.html() for _ in page_fields]),
		"action_url": '/__meta/settings?page=' + page_name
	})
