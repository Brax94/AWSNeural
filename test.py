from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import werkzeug
from PIL import Image
import keras
from keras.applications.nasnet import NASNetMobile
from keras.preprocessing import image
import numpy as np
import json
import tensorflow as tf
from keras.applications.imagenet_utils import preprocess_input, decode_predictions


def load_model():
	global model
	print('Loading model')
	model = NASNetMobile(weights=None)
	model.load_weights(
		'nasnet.h5')
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
				processImage(photo.stream)
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
	img = image.load_img(img, target_size=(224, 224))
	# Preprocessing the image
	x = image.img_to_array(img)
	x = (x/127.5) - 1
	# x = np.true_divide(x, 255)
	x = np.expand_dims(x, axis=0)

	# Be careful how your trained model deals with the input
	# otherwise, it won't make correct prediction!
	#x = preprocess_input(x, mode='caffe')

	with graph.as_default():
		preds = model.predict(x)
	num = np.argmax(preds)
	print classes[num]

load_model()

api.add_resource(Test, '/test')
api.add_resource(HandleImage, '/HandleImage')


if __name__ == '__main__':
	pass
	#app.run(host="0.0.0.0", port=80)
	#app.run(host="0.0.0.0/", port=80)