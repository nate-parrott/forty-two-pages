from app import db
import util
import os
import util
import settings
from BeautifulSoup import BeautifulSoup, Tag
import datetime
import themes
import flask

class MongoObject(object):
	collection = None
	lazy = False # lazy objects are not created until update() is called. they may not have '_id' values
	def load_record(self, unique_dict):
		self.record = self.collection.find_one(unique_dict)
		if self.record == None:
			self.create_record(unique_dict)
	
	def id(self):
		self.insert_record_if_needed()
		return self.record['_id']
	
	def create_record(self, unique_dict=None):
		self.record = dict(unique_dict) if unique_dict else {}
		self.initialize_record()
		if not self.lazy:
			self.insert_record_if_needed()
	
	def insert_record_if_needed(self):
		if '_id' not in self.record:
			self.record['_id'] = self.collection.insert(self.record)
	
	def initialize_record(self):
		self.record['created'] = datetime.datetime.now()
		self.record['last_updated'] = datetime.datetime.now()
	
	def update(self, dictionary):
		self.insert_record_if_needed()
		dictionary = dict(dictionary)
		dictionary['last_updated'] = datetime.datetime.now()
		self.collection.update({"_id": self.record['_id']}, {"$set": dictionary})
		for k, v in dictionary.iteritems():
			self.record[k] = v


class Site(MongoObject):
	lazy = True
	
	collection = db.sites
	@staticmethod
	def current():
		return Site(util.site())
	
	@staticmethod
	def exists(name):
		return db.sites.find_one({"name": name.lower()}) != None
	
	def __init__(self, name):
		self.load_record({"name": name.lower()})
	
	def delete(self):
		db.pages.remove({'site': self.record['name']})
		db.sites.remove({'name': self.record['name']})
	
	def wrap_html_with_site_theme(self, html):
		theme = Page(self, 'theme')
		magic_string = "NFNIFHUIFGPRIUGWRPIWR" # TODO: there _must_ be a better way to do this
		theme_soup = BeautifulSoup(theme.record['source'])
		content_placeholder = theme_soup.find(id='PAGE_CONTENT_HERE')
		if content_placeholder:
			content_placeholder.replaceWith(magic_string)
		text = unicode(theme_soup)
		text = text.replace(magic_string, "<div id='__content'>" + html + "</div>")
		return text

import embed

class Page(MongoObject):
	collection = db.pages
	def __init__(self, site, page, lazy=False):
		self.lazy = lazy
		self.load_record({"site": site.record['name'], "name": page})
	
	def initialize_record(self):
		super(Page, self).initialize_record()
		page = self.record['name']
		site = self.record['site']
		name = page if page != '' else site
		if self.record['name'] == 'theme':
			default_theme = themes.Theme.named("Centered")
			ct = default_theme.get_theme_content()
			self.record['source'] = ct['html']
			self.record['css'] = ct['css']
			self.record['js'] = ct['js']
			self.record['title'] = "Site layout"
		else:
			self.record['source'] = "<h1>%s</h1>\n<p>[your text here]</p>"%(name)
			self.record['title'] = page.split('/')[-1] if page!='' else site
	
	def wrap_source_with_theme(self, preserve_source=False):
		html = self.record['source']
		if self.theme():
			return self.site().wrap_html_with_site_theme(html)
		else:
			return html
	
	def site(self):
		return Site(self.record['site'])
	
	def theme(self):
		if self.record['name'] == 'theme':
			return None
		else:
			return Page(self.site(), 'theme')
	
	def render(self, editing, preserve_source=False):
		wrapped_source = self.wrap_source_with_theme(preserve_source=preserve_source)
		soup = BeautifulSoup(wrapped_source)
		if not editing:
			for file_element in soup.findAll(attrs={'download-url': True}):
				tag = Tag(soup, "a")
				tag['href'] = file_element['download-url']
				#tag['download'] = file_element['download-url'].split('/')[-1]
				file_element.replaceWith(tag)
				tag.insert(0, file_element)
			"""for placeholder in soup.findAll(attrs={'data-embed-id': True}):
				placeholder.replaceWith(util.soup_for_fragment_inside_div(embed.Embed.WithId(placeholder['data-embed-id']).render(), "style='display: inline-block'"))"""
		return unicode(soup)
	

