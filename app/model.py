from app import db
import util
import os
import util
import settings
from BeautifulSoup import BeautifulSoup, Tag
import datetime

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
			util.log("INSERTING RECORD " + str(self.record))
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


DEFAULT_CSS = util.data_file('defaultCSS.css')

class Page(MongoObject):
	collection = db.pages
	def __init__(self, site, page, lazy=False):
		self.lazy = lazy
		self.load_record({"site": site.record['name'], "name": page})
	
	def initialize_record(self):
		page = self.record['name']
		site = self.record['site']
		name = page if page != '' else site
		self.record['source'] = "<h1>%s</h1>\n<p>[your text here]</p>"%(name)
		self.record['title'] = page.split('/')[-1] if page!='' else site
		self.record['css'] = DEFAULT_CSS
	
	def render(self):
		source = self.record['source']
		soup = BeautifulSoup(source)
		for file_element in soup.findAll(attrs={'download-url': True}):
			tag = Tag(soup, "a")
			tag['href'] = file_element['download-url']
			#tag['download'] = file_element['download-url'].split('/')[-1]
			file_element.replaceWith(tag)
			tag.insert(0, file_element)
		return unicode(soup)
