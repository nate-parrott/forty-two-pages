from app import db
import util

class MongoObject(object):
	collection = None
	def load_record(self, unique_dict):
		self.record = self.collection.find_one(unique_dict)
		if self.record == None:
			self.record = dict(unique_dict) # copy it
			self.initialize_record()
			self.record['_id'] = self.collection.insert(self.record)
	
	def initialize_record(self):
		pass
	
	def update(self, dictionary):
		self.collection.update({"_id": self.record['_id']}, {"$set": dictionary})
		for k, v in dictionary.iteritems():
			self.record[k] = v


class Site(MongoObject):
	collection = db.sites
	@staticmethod
	def current():
		return Site(util.site())
	
	def __init__(self, name):
		self.load_record({"name": name})


class Page(MongoObject):
	collection = db.pages
	def __init__(self, site, page):
		self.load_record({"site": site.record['name'], "name": page})
	
	def initialize_record(self):
		page = self.record['name']
		site = self.record['site']
		self.record['source'] = "<h1>[your site here]</h1>\n<p>click the gear to edit</p>"
		self.record['title'] = page.split('/')[-1] if page!='' else site
	
	def render(self):
		return self.record['source']

