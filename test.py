from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import werkzeug
from PIL import Image
import keras
from keras.applications.nasnet import NASNetMobile
import numpy as np
import json
import tensorflow as tf


def load_model():
	global model
	print('Loading model')
	model = NASNetMobile(weights=None)
	model.load_weights(
		'/jet/prs/nasnet.h5')
	print('Loaded model')
	global graph
	graph = tf.get_default_graph()

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('file',type=werkzeug.datastructures.FileStorage, location='files')
class Test(Resource):
	def get(self):
		return "Hello World"

ALLOWED_TYPES = {"image/png", "image/JPEG", "image/jpeg", "image/jpg"}

classes = {}
with open('classes.txt') as f:
	for line in f:
		mstr = str(line)
		mstr = mstr.replace('{', '')
		mstr = mstr.replace('}', '')
		(key, val) = mstr.split(':')
		if key != 999:
			val = val[:-1]
		classes[int(key)] = val


class HandleImage(Resource):
	def post(self):
		data = parser.parse_args()
		print (data)
		if data['file'] == "" or data['file'] == None:
			return "Data not found"
		photo = data['file']
		if photo:
			print (photo)
			retDat = {
			'filename': photo.filename,
			'mimetype': photo.mimetype,
			'status': 'success' }
			if photo.mimetype in ALLOWED_TYPES:
				imageToProcess = Image.open(photo.stream)
				processImage(imageToProcess)
			else:
				retDat['status'] = 'failure'
				retDat['reason'] = 'not an image'
			return retDat
		else:
			return "ERROR: Could not find file"

@app.errorhandler(404)
def page_not_found(e):
		return "Quote the server, 404,-", 404


def processImage(img):
	img = img.resize((224,224))
	img.show()
	img = np.asarray(img)[None, ...]
	img = img / (img.max() / 2) - 1
	with graph.as_default():
		num = np.argmax(model.predict(img[None, ...]))
	print (classes[num])
load_model()

api.add_resource(Test, '/test')
api.add_resource(HandleImage, '/HandleImage')


if __name__ == '__main__':
	pass
	#app.run(host="0.0.0.0", port=80)
	#app.run(host="0.0.0.0/", port=80)