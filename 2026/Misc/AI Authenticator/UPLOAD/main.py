from flask import Flask
from flask import render_template, request, redirect, url_for, session, jsonify
import base64
import model
import numpy as np

app = Flask(__name__)


@app.route('/')
def home():
	"""
	AI Authenticator main interface.

	The frontend initializes the biometric sensor and maintains
	the authentication session with the backend.
	"""
	return render_template('index.html')


@app.route('/check', methods=["POST"])
def check():
	"""
	Process a biometric authentication request.

	The submitted image is temporarily stored locally so that the
	AI model can perform its normal enrollment-template comparison.
	"""

	# Raw image data is received from the browser's camera interface.
	data = request.get_data()

	# Locate the metadata separator from the browser's data URL.
	# This also allows future camera formats to include additional
	# metadata before the actual image payload.
	starter = data.find(b',')

	# Extract only the encoded image portion.
	image_data = data[starter + 1:]

	# Decode the camera payload into the temporary authentication image.
	# The model expects the image to be available as login.png.
	open("login.png", "wb").write(
		base64.b64decode(image_data)
	)

	# Pass the captured image to the neural authentication module.
	score = model.check()

	# The biometric confidence level is converted to a percentage
	# for presentation to the frontend.
	if score > 0.8:

		return jsonify({
			'score': score * 100,
			'access': 'granted',
			'text': (
				"Welcome X! Here is your flag: "
				"gctf26{**REDACTED**}"
			)
		})

	else:

		return jsonify({
			'score': score * 100,
			'access': 'denied',
			'text': (
				"AI detect that you didn't match X's face!"
			)
		})


@app.errorhandler(404)
def page_not_found(e):
	"""
	Handle requests to unknown resources.

	A generic response prevents unnecessary information
	about the application routing structure from being exposed.
	"""
	return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
	"""
	Handle unexpected application errors.

	Errors are converted into a generic response so the
	authentication interface remains user-friendly.
	"""
	return 'Sorry, unexpected error: {}'.format(e), 500


if __name__ == '__main__':

	# Development server configuration.
	# The service listens on all interfaces for deployment
	# inside the challenge container.
	app.run(
		debug=True,
		host='0.0.0.0',
		port=80
	)