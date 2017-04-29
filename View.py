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

class MainView:
	def __init__(self, vs, recognizer, width=320, height=450, framerate=32, videoduration=3):

		self.state = 0
		
		self.vs = vs
		self.outputPath = "outputPath"
		self.frame = None
		self.thread = None
		self.stopVideoLoop = None

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
		self.textFont = tkFont.Font(family='Helvetica', size=18, weight='normal')

		self.button = tki.Button(text=u"\u266C", command=self.ring, font=self.headerFont)
		self.button.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)

		self.textPanel = tki.Label(self.container, text="Hello, world", font=self.textFont)

		self.showVideo = True

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

	def videoLoop(self):
		try:
			while (not self.stopVideoLoop.is_set()):
				if self.state == 0:
					time.sleep(self.sleepduration*3)
				elif self.state == 1:
					self.frame = self.vs.read()
					iframe = imutils.resize(self.frame, width=self.panelWidth)
					iframe = cv2.flip(iframe,1)

					if not self.videoText == None:
						self.recognizer.draw_str(iframe, (self.panelWidth/2,iframe.shape[0]), self.videoText)
					
					image = cv2.cvtColor(iframe, cv2.COLOR_BGR2RGB)

					faces = self.recognizer.detect_faces(image)

					for face in faces:
						x0, y0, h, w = [result for result in face]
						x1 = x0 + w
						y1 = y0 + h
						cv2.rectangle(image, (x0,y0),(x1,y1),(0,234,12),1)

					image = Image.fromarray(image)
					image = ImageTk.PhotoImage(image)
					
					if self.panel is None:
						self.textPanel['text'] = 'Please show \nyour face clearly. \nA green rectangle \nwill appear \naround your face.'
						self.textPanel['fg'] = '#a71c34'
						self.textPanel.pack(in_=self.container, side="bottom", fill="both", expand="yes", padx=10, pady=10)
						self.panel = tki.Label(self.container,image=image)
						self.panel.image = image
						self.panel.pack(side="left", padx=0, pady=0)
					else:
						self.panel.configure(image=image)
						self.panel.image = image

					#Video Recording
					if (not self.video == None) and self.videoRecord > 0:
						self.videoRecord -= 1
						self.video.write(self.frame)

						if self.videoRecord == 0:
							self.video.release()
							self.video = None
							#os.system('ffmpeg -i output.avi output.mp4')
							FNULL = open(os.devnull, 'w')
							subprocess.call('ffmpeg -i output.avi output.mp4', shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
							FNULL = None
				time.sleep(self.sleepduration)

		except RuntimeError, e:
			print("[INFO] caught a RuntimeError")

	def ring(self):
		self.state = 1
		self.button.pack_forget()

		# recognized = self.recognizer.recognize(self.frame)
		# #self.button.configure(text="red", background = "red")

		# if len(recognized) > 0:
		# 	recognized_id, prediction = recognized[0]

		# 	if not recognized_id == None:
		# 		self.videoText = self.recognizer.people[recognized_id]
		# else:
		# 	self.videoText = "I don't know you!"
		
		# #self.showVideo = not self.showVideo
	
		# self.button.pack_forget()
		# self.panel.pack_forget()
		# time.sleep(2)
		# self.panel.pack()
		# self.button.pack()

		# print('Ringed the bell!')

	def onClose(self):
		print("[INFO] Closing")
		self.stopVideoLoop.set()
		self.vs.stop()
		#self.root.destroy()
		self.root.quit()

	def initVideo(self):
		self.videoRecord = self.videoDuration

		try:
			os.remove('output.avi')
			os.remove('output.mp4')
		except OSError:
			pass

		self.video = cv2.VideoWriter('output.avi', self.videoCodec, self.framerate/2, (self.frame.shape[1],self.frame.shape[0]))

