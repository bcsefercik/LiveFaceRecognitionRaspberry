"""
	Bugra Can Sefercik
	ELEC 491 Term Project
	Face Recognizer Class
	21 April 2017
"""

import os
import numpy as np
import cv2

MODEL_FILE = 'model.mdl'

class Recognizer:

	def load_images(self):
		images, labels = [], []
		c = 0
		for dirname, dirnames, filenames in os.walk(self.data):
			for subdirname in dirnames:
				if not subdirname == 'ex':
					subjectPath = os.path.join(dirname, subdirname)
					#print str(c) + " - " + subdirname
					self.people[c] = subdirname
					for filename in os.listdir(subjectPath):
						file = os.path.join(subjectPath, filename)
						filename, file_extension = os.path.splitext(file)
						if file_extension == '.jpg':
							#print(file)
							try:
								img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
								img = cv2.resize(img, (100,100))
								images.append(np.asarray(img, dtype=np.uint8))
								labels.append(c)
							except IOError, (errno, strerror):
								print "IOError({0}): {1}".format(errno, strerror)
							except:
								print "Unexpected error"
					c += 1
			#print(self.people)
			return images, np.array(labels)

	def get_faces(self, img):
		return self.cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

	def save_faces_img(self, prefix, img):
		faces = self.get_faces(img)
		c = 0
		for face in faces:
			x, y, h, w = [result for result in face]
			cv2.imwrite(prefix+str(a)+str(c)+".jpg",img[y:y+h,x:x+w])
			c += 1
		self.face_checked =+ 1

	def load_model(self):
		#model = cv2.createFisherFaceRecognizer()
		model = cv2.createLBPHFaceRecognizer()
		images, labels = self.load_images()
		if not self.modelFile == None:
			model.load(self.modelFile)
		else:
			model.train(images, labels)
			model.save(MODEL_FILE)
		return model

	def train(self):
		return self.load_model()

	def recognize(self, img):
		faces = self.get_faces(img)
		if len(faces) > 0:
			i = 1
			for face in faces:
				x, y, h, w = [result for result in face]
				resized = cv2.resize(img[y:y+h,x:x+w], (100,100))
				return self.model.predict(resized)
		return None, None

	def detectFaces(self, image):
		gray = to_gray(img)
		rects = self.cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

		if len(rects) == 0:
			return []
		return rects

	def draw_str(self, dst, (x, y), s):
		fontSize = 2.0
		textSize, baseline = cv2.getTextSize(s, cv2.FONT_HERSHEY_DUPLEX, fontSize, thickness = 2) 
		x = x - textSize[0]/2
		y = y - textSize[1]
		cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_DUPLEX, fontSize, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
		cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_DUPLEX, fontSize, (255, 255, 255), lineType=cv2.CV_AA)


	def to_gray(self, img):
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		gray = cv2.equalizeHist(gray)
		return gray


	def __init__(self, modelFile=None, data='data', cascadePath = 'haarcascade_frontalface_default.xml'):
		self.modelFile = modelFile
		#self.model = cv2.createFisherFaceRecognizer()
		self.cascade = cv2.CascadeClassifier(cascadePath)
		self.data = data
		self.people = {}
		self.face_checked = 0
		self.model = self.load_model()