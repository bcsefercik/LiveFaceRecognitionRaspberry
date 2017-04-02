from imutils.video import VideoStream
import os
import numpy as np
import imutils
import time
import cv2

onPi = False

vs = VideoStream(usePiCamera=onPi).start()

#time.sleep(2.0)

MODEL_FILE = "model.mdl"
path = 'data'

def to_gray(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	gray = cv2.equalizeHist(gray)
	return gray

def load_images(path):
	images, labels = [], []
	c = 0
	print "test " + path
	for dirname, dirnames, filenames in os.walk(path):
		print "test"
		for subdirname in dirnames:
			subjectPath = os.path.join(dirname, subdirname)
			print str(c) + " - " + subdirname
			for filename in os.listdir(subjectPath):
				try:
					img = cv2.imread(os.path.join(subjectPath, filename), cv2.IMREAD_GRAYSCALE)
					img = cv2.resize(img, (100,100))
					images.append(np.asarray(img, dtype=np.uint8))
					labels.append(c)
				except IOError, (errno, strerror):
					print "IOError({0}): {1}".format(errno, strerror)
				except:
					print "Unexpected error:" , sys.exc_info()[0]
					raise
			c += 1
		return images, np.array(labels)

def detect(img, cascade):
	gray = to_grayscale(img)
	rects = cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)

	if len(rects) == 0:
		return []
	return rects

def save_faces(path, cascade):
	images, labels = [], []
	c = 0
	print "test " + path
	for dirname, dirnames, filenames in os.walk(path):
		for subdirname in dirnames:
			print str(c) + " - " + subdirname
			subjectPath = os.path.join(dirname, subdirname)
			for filename in os.listdir(subjectPath):
				try:
					filepath = os.path.join(subjectPath, filename)
					img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
					i = 1
					faces = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
					for face in faces:
						x, y, h, w = [result for result in face]
						cv2.imwrite(os.path.join(subjectPath, "face_") + filename + "_" + str(i) + ".jpg" ,img[y:y+h,x:x+w])
						i += 1
				except IOError, (errno, strerror):
					print "IOError({0}): {1}".format(errno, strerror)
				except:
					print "Unexpected error:"
					raise
			c += 1


def get_faces(img, cascade):
	return cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags = cv2.CASCADE_SCALE_IMAGE)
	

def save_faces_img(prefix,img, cascade):
	faces = get_faces(img, cascade)
	c = 0
	for face in faces:
		x, y, h, w = [result for result in face]
		cv2.imwrite(prefix+str(c)+".jpg",img[y:y+h,x:x+w])
		c += 1

def load_model(file=None):
	model = cv2.createFisherFaceRecognizer()
	if file != None:
		model.load(MODEL_FILE)
		print "Trained model loaded."
	return model

def train():
	images, labels = load_images(path)
	model = load_model()
	model.train(images,labels)
	model.save(MODEL_FILE)
	print labels
	return model

def recognize(img, cascade, model):
	faces = get_faces(img, cascade)
	if len(faces)>0:
		i = 1
		for face in faces:
			x, y, h, w = [result for result in face]
			resized = cv2.resize(img[y:y+h,x:x+w], (100,100))
			recognized = model.predict(resized)
			print recognized


faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

#save_faces(path, faceCascade)

model = train()






while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
	frame = to_gray(frame)

	
	# draw the timestamp on the frame
	#timestamp = datetime.datetime.now()
	#ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	#cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
	elif key == ord("d"):
		save_faces_img("face", frame, faceCascade)
	elif key == ord("r"):
		recognize(frame, faceCascade, model)

	time.sleep(0.04)