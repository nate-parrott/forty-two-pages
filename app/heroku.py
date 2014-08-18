import requests
import base64
import util

API_TOKEN = "541cfc9701806d5f038e9e8819ff2e881f9119ba"

headers = {
	"Accept": "application/vnd.heroku+json; version=3",
	"Authorization": "Basic " + base64.b64encode(":" + API_TOKEN)
}

root = "https://api.heroku.com/apps/forty-two-pages"

def add_domain(domain):
	r = requests.post(root+"/domains", data={"hostname": domain}, headers=headers)
	util.log(r.text)
	util.log('code: %i'%r.status_code)
	return r.status_code == 201
