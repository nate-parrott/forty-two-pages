from app import app, templ8
import flask
import model
import permissions
import util

@permissions.protected
@app.route('/__meta/moderate', methods=['GET', 'POST'])
def moderate():
	if util.site() != 'moderator':
		return flask.redirect('http://moderator.42pag.es/__meta/moderate')
	
	if flask.request.method=='POST':
		site_name = flask.request.form.get('site', '')
		site = model.Site(site_name)
		action = flask.request.form.get('action', '')
		util.log("ACTION: " + action)
		if action == 'Delete':
			site.delete()
			return flask.redirect('http://42pag.es')
		elif action == 'Gain edit access':
			return flask.redirect(permissions.generate_access_url(site, permissions.MASTER_KEY_EMAIL))
	
	return templ8("moderate.html", {"site": flask.request.args.get('site', '')})
