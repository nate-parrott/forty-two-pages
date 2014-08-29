from app import app
import tinys3
from werkzeug import secure_filename
import os
import uuid
import json
import flask
from flask import request
import os
import util
import permissions

S3_KEY = "AKIAJKHOHZKDFQEKWPXA"
S3_SECRET = "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"

@app.route('/__meta/upload', methods=['POST'])
@permissions.protected
def upload():
	conn = tinys3.Connection(S3_KEY, S3_SECRET)
	file = request.files['file']
	name = secure_filename(file.filename)
	s3_name = 'uploads/' + str(uuid.uuid4()) + '/' + name
	conn.upload(s3_name, file, "easyaf")
	return json.dumps({"name": name, "url": "https://s3.amazonaws.com/easyaf/" + s3_name, "mimetype": file.mimetype})

FILE_IMAGE_SVG = util.data_file('fileImage.svg')
@app.route('/__meta/fileImage/<filename>')
def file_image(filename):
	svg = FILE_IMAGE_SVG.replace('<!--filename-->', filename)
	response = flask.make_response(svg)
	response.headers['Content-Type'] = 'image/svg+xml'
	return response
