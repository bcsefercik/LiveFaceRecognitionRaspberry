from PIL import Image
from PIL import ImageTk
import Tkinter as tki
import threading
import imutils
import time
import cv2

class MainView:
	def __init__(self, vs, recognizer, width=320, height=450, framerate=32):
		
		self.vs = vs
		self.outputPath = "outputPath"
		self.frame = None
		self.thread = None
		self.stopVideoLoop = None

		self.root = tki.Tk()
		self.root.resizable(width=False, height=False)
		self.root.geometry('{}x{}'.format(width, height))
		self.panel = None
		self.panelWidth = width

		self.framerate = framerate
		self.sleepduration = 1.0/self.framerate

		self.button = tki.Button(self.root, text="Ring the Bell!", command=self.ring)
		self.button.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

		self.showVideo = True

		self.stopVideoLoop = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		self.root.wm_title("Hoosthere")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

		self.recognizer = recognizer

		self.videoText = None


	def videoLoop(self):
		try:
			while (not self.stopVideoLoop.is_set()):
				if self.showVideo:
					self.frame = self.vs.read()
					iframe = imutils.resize(self.frame, width=self.panelWidth)
					
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
						self.panel = tki.Label(image=image)
						self.panel.image = image
						self.panel.pack(side="left", padx=0, pady=0)
					else:
						self.panel.configure(image=image)
						self.panel.image = image

		except RuntimeError, e:
			print("[INFO] caught a RuntimeError")

	def ring(self):
		recognized = self.recognizer.recognize(self.frame)

		if len(recognized) > 0:
			recognized_id, prediction = recognized[0]

			if not recognized_id == None:
				self.videoText = self.recognizer.people[recognized_id]
		else:
			self.videoText = "I don't know you!"
		
		#self.showVideo = not self.showVideo
		#print(self.showVideo)

		print('Ringed the bell!')
		return 0

	def onClose(self):
		print("[INFO] Closing")
		self.stopVideoLoop.set()
		self.vs.stop()
		self.root.destroy()
		self.root.quit()