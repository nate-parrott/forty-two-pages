from app import app, db, model, templ8
import pymongo

@app.route('/__meta/index/<page>')
@app.route('/__meta/index')
def index(page=0):
	page = int(page)
	page_size = 40
	cursor = db.sites.find(skip=page_size * page, limit=page_size + 1).sort("_id", pymongo.DESCENDING)
	items = list(cursor)
	has_more = len(items) > page_size
	items = items[:min(page_size, len(items))]
	next_page = "/__meta/index/"+str(page+1) if has_more else None
	prev_page = "/__meta/index/"+str(page-1) if page > 0 else None
	return templ8("index.html", {
		"next": next_page,
		"prev": prev_page,
		"items": items
	})
