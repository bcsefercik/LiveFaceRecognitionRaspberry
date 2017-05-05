from PIL import Image
from PIL import ImageTk
import Tkinter as tki
import tkFont
import threading
import imutils
import time
import cv2
import os
import subprocess
import boto3
import boto3.session
import bcssns as sns
import requests


class MainView:
	def __init__(self, vs, recognizer, width=320, height=450, framerate=32, videoduration=3):
		self.endpoint = 'http://localhost:8000/hoo/'
		self.endpoint = 'http://hoo-dev.eu-central-1.elasticbeanstalk.com/hoo/'
		self.state = 0

		self.session = boto3.session.Session(region_name='eu-central-1')
		self.s3 = boto3.resource('s3')
		self.videoS3Name = ''
		
		self.vs = vs
		self.outputPath = "outputPath"
		self.frame = self.vs.read()
		self.thread = None
		self.stopVideoLoop = None
		self.peopleCount = 0

		self.root = tki.Tk()
		self.root.resizable(width=False, height=False)
		self.root.geometry('{}x{}'.format(width, height))

		self.container = tki.Frame(self.root)
		self.container.pack(side="top", fill="both", expand=True)

		self.panel = None
		self.panelWidth = width

		self.framerate = framerate
		self.sleepduration = 1.0/self.framerate

		self.headerFont = tkFont.Font(family='Helvetica', size=130, weight='bold')
		self.subHeaderFont = tkFont.Font(family='Helvetica', size=26, weight='bold')
		self.textFont = tkFont.Font(family='Helvetica', size=18, weight='normal')

		self.button = tki.Button(text=u"\u266C", command=self.ring, font=self.headerFont)
		self.buttonPacked = False

		self.textPanel = tki.Label(self.container, text="Hello, world", font=self.textFont)
		self.messageText = tki.Text(self.container, font=self.textFont)

		self.stopVideoLoop = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		self.root.wm_title("Hoosthere")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

		self.recognizer = recognizer

		self.videoText = None
		self.videoDuration = videoduration*self.framerate/2
		self.videoRecord = 0
		self.videoCodec = cv2.cv.CV_FOURCC(*'MJPG')
		self.video = None

		self.predictions = []

		self.message = ''

		self.recognizedPerson = -1
		self.catDetected = 0
	def videoLoop(self):
		try:
			while (not self.stopVideoLoop.is_set()):
				if self.state == 0:
					self.peopleCount = 0
					if not self.buttonPacked:
						self.button.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)
						self.buttonPacked = True

					self.frame = self.vs.read()
					iframe = imutils.resize(self.frame, width=self.panelWidth)
					iframe = cv2.flip(iframe,1)					
					image = cv2.cvtColor(iframe, cv2.COLOR_BGR2RGB)

					catCount, cats = self.recognizer.detect_cats(image)

					if catCount > 0:
						self.videoRecord = int(self.videoDuration*0.75)
						self.catDetected = catCount
						print('INFO: Cat detected.')
						print('STATE: 0 -> 13')
						self.button.pack_forget()
						self.buttonPacked = False
						self.initVideo()
						self.state = 13

					time.sleep(self.sleepduration*3)
				elif self.state == 1:
					self.frame = self.vs.read()
					iframe = imutils.resize(self.frame, width=self.panelWidth)
					iframe = cv2.flip(iframe,1)
					if not self.videoText == None:
						self.recognizer.draw_str(iframe, (self.panelWidth/2,iframe.shape[0]), self.videoText)
					
					image = cv2.cvtColor(iframe, cv2.COLOR_BGR2RGB)

					faces = self.recognizer.detect_faces(image)

					if self.videoRecord == 0 and len(faces) > 0:
						self.videoRecord = self.videoDuration
						print('INFO: Started video recording.')

					self.peopleCount = max(len(faces), self.peopleCount)
					for face in faces:
						x0, y0, h, w = [result for result in face]
						x1 = x0 + w
						y1 = y0 + h
						cv2.rectangle(image, (x0,y0),(x1,y1),(0,234,12),1)

					catCount, cats = self.recognizer.detect_cats(image)
					for cat in cats:
						x0, y0, h, w = [result for result in cat]
						x1 = x0 + w
						y1 = y0 + h
						cv2.rectangle(image, (x0,y0),(x1,y1),(136,46,120),2)

					image = Image.fromarray(image)
					image = ImageTk.PhotoImage(image)
					
					if self.panel is None:
						self.textPanel['text'] = 'Please show \nyour face clearly. \nA green rectangle \nwill appear \naround your face.'
						self.textPanel['fg'] = '#a71c34'
						self.textPanel['font'] = self.textFont
						self.textPanel.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)
						self.panel = tki.Label(self.container,image=image)
						self.panel.image = image
						self.panel.pack(side="left", padx=0, pady=0)
					else:
						self.panel.configure(image=image)
						self.panel.image = image

					if self.videoRecord != 0 and self.videoRecord%5 == 0 and self.peopleCount > 0:
						self.predictions.append(self.recognizer.recognize(self.frame))
						print('INFO: Calling recognize()')

					#Video Recording
					if (not self.video == None) and self.videoRecord > 0:

						self.videoRecord -= 1
						self.video.write(self.frame)

						if self.videoRecord <= 0:
							self.video.release()
							self.video = None
							print('INFO: Video saved.')
							#os.system('ffmpeg -i output.avi output.mp4')
							FNULL = open(os.devnull, 'w')
							subprocess.call('ffmpeg -i output.avi output.mp4', shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
							FNULL = None
							print('INFO: Video conversion is completed.')

							#Moving to next state.
							self.panel.pack_forget()
							self.panel = None
							self.textPanel.pack_forget()
							print('STATE: 1 -> 2')
							self.state = 2
					time.sleep(self.sleepduration)
				elif self.state == 2:
					print('INFO: Uploading video.')

					if self.textPanel['text'] == '':
						self.textPanel['text'] = u"\u0489" + '\n\nProcessing...'
						self.textPanel['font'] = self.textFont
						self.textPanel.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)

					data = open('output.mp4', 'rb')
					self.videoS3Name = str(int(round(time.time() * 1000)))
					self.s3.Bucket('hoo-bucket').put_object(Key=self.videoS3Name + '.mp4', Body=data, ACL='public-read')
					data = None
					print('INFO: Video uploaded.')
					print('INFO: Video ID: ' + self.videoS3Name)
					print('INFO: Predictions: ')
					print(self.predictions)
					
					self.textPanel['text'] = ''
					self.textPanel.pack_forget()
					state = 2
					if self.peopleCount > 0:
						state, self.recognizedPerson = self.evalPredictions()
						r = requests.post(self.endpoint + 'create_visit/', json={'username': self.recognizedPerson, 'video_id': self.videoS3Name})
						print(r)
						sns.send_push(body= self.recognizedPerson + ' at the door.', device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
		
						self.peopleCount = 0
					else:
						state = 14

					self.peopleCount = 0
					self.catDetected = 0
					print('STATE: 2 -> ' + str(state))
					self.state = state
				elif self.state == 3:
					#Recognized check for message
					#self.recognizedPerson deletion

					self.state = 10
					self.messageText['bd'] = 0
					self.messageText.insert(tki.END, "Denemeeeeeeeee")
					self.messageText['state'] = tki.DISABLED

					self.messageText.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					time.sleep(5)
					self.messageText['state'] = tki.NORMAL
					self.messageText.delete(1.0, tki.END)
					self.messageText.pack_forget()
					self.catDetected = 0
					self.peopleCount = 0
					print('STATE: 3 -> 10')
					self.state = 10
				elif self.state == 4:
					# check for voice
					self.state = 11
				elif self.state == 5:
					#wait for answer
					self.state = 11
				elif self.state == 10:
					#access granted check w/wo message
					if self.textPanel['text'] == '':
						self.textPanel['text'] = 'Access Granted'
						self.textPanel['font'] = self.subHeaderFont
						self.textPanel['fg'] = '#26C281'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					time.sleep(5)
					self.textPanel['text'] = ''
					self.textPanel.pack_forget()

					print('STATE: 10 -> 0')
					self.state = 0
				elif self.state == 13:
					#TODO cat notif

					self.frame = self.vs.read()
					iframe = imutils.resize(self.frame, width=self.panelWidth)
					iframe = cv2.flip(iframe,1)
					
					image = cv2.cvtColor(iframe, cv2.COLOR_BGR2RGB)

					catCount, cats = self.recognizer.detect_cats(image)
					for cat in cats:
						x0, y0, h, w = [result for result in cat]
						x1 = x0 + w
						y1 = y0 + h
						cv2.rectangle(image, (x0,y0),(x1,y1),(136,46,120),2)

					image = Image.fromarray(image)
					image = ImageTk.PhotoImage(image)
					
					if self.panel is None:
						self.panel = tki.Label(self.container,image=image)
						self.panel.image = image
						self.panel.pack(side="left", padx=0, pady=0)
					else:
						self.panel.configure(image=image)
						self.panel.image = image

					if (not self.video == None) and self.videoRecord > 0:
						self.videoRecord -= 1
						self.video.write(self.frame)

						if self.videoRecord <= 0:
							self.video.release()
							self.video = None
							print('INFO: Video saved.')
							#os.system('ffmpeg -i output.avi output.mp4')
							FNULL = open(os.devnull, 'w')
							subprocess.call('ffmpeg -i output.avi output.mp4', shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
							FNULL = None
							print('INFO: Video conversion is completed.')

							#Moving to next state.
							self.panel.pack_forget()
							self.panel = None
							print('STATE: 13 - > 2')
							self.state = 2
					time.sleep(self.sleepduration)
				elif self.state == 14:
					#access granted check w/wo message
					sns.send_push(body= 'Cat is home.', device_id = 'd8f936c3d186d37f232e5c1d7e139a8f0f86e9ba62ed91f0657997b0464f568e')
					if self.textPanel['text'] == '':
						self.textPanel['text'] = 'Cat\nAccess\nGranted'
						self.textPanel['font'] = self.subHeaderFont
						self.textPanel['fg'] = '#882E78'
						self.textPanel.pack(in_=self.container, side="top", fill="both", expand="yes", padx=10, pady=10)

					time.sleep(5)
					self.textPanel['text'] = ''
					self.textPanel.pack_forget()

					print('STATE: 14 -> 0')
					self.state = 0
				else:
					print(212)
					time.sleep(5)

		except RuntimeError, e:
			print("INFO: caught a RuntimeError")

	def ring(self):
		self.state = 1
		self.button.pack_forget()
		self.buttonPacked = False
		self.initVideo()
		print('INFO: Ringed the bell!')

	def onClose(self):
		print("INFO: Closing")
		self.stopVideoLoop.set()
		self.vs.stop()
		#self.root.destroy()
		self.root.quit()

	def initVideo(self):

		try:
			os.remove('output.avi')
			os.remove('output.mp4')
		except OSError:
			pass

		self.video = cv2.VideoWriter('output.avi', self.videoCodec, self.framerate/2, (self.frame.shape[1],self.frame.shape[0]))

	def evalPredictions(self, picthreshold=100, voicethreshold=75):
		picMul = 0.5
		voiceMul = 0.68
		scoresPic = {}
		scoresVoice = {}

		state = -1
		person = -1
		numInstance = len(self.predictions)
		picMul = int(picMul*numInstance)
		voiceMul = int(voiceMul*numInstance)

		for ps in self.predictions:
			for p in ps:
				if p[1] < picthreshold:
					if not p[0] in scoresPic.keys():
						scoresPic[p[0]] = 1
					else:
						scoresPic[p[0]] += 1
				elif p[1] < voicethreshold:
					if not p[0] in scoresVoice.keys():
						scoresVoice[p[0]] = 1
					else:
						scoresVoice[p[0]] += 1

		self.predictions = []

		if len(scoresPic) == 0 and len(scoresVoice) == 0:
			state = 8
			return state, person

		maxIndex = scoresPic.values().index(max(scoresPic.values()))
		maxID = scoresPic.keys()[maxIndex]
                
		person = maxID
		if scoresPic[person] >= picMul:
			state = 3
		elif (scoresPic[person] + scoresVoice[person]) >= voiceMul:
			state = 4
		else:
			person = -1
			state = 5

		return state, self.recognizer.people[person]

