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
		self.stopEvent = None

		self.root = tki.Tk()
		self.root.resizable(width=False, height=False)
		self.root.geometry('{}x{}'.format(width, height))
		self.panel = None
		self.panelWidth = width

		self.framerate = framerate
		self.sleepduration = 1.0/self.framerate

		btn = tki.Button(self.root, text="Snapshot!",
			command=self.takeSnapshot)
		btn.pack(side="bottom", fill="both", expand="yes", padx=10,
			pady=10)

		self.stopEvent = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		self.root.wm_title("PyImageSearch PhotoBooth")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

		self.recognizer = recognizer

	def videoLoop(self):
		try:
			while not self.stopEvent.is_set():
				self.frame = self.vs.read()
				self.frame = imutils.resize(self.frame, width=self.panelWidth)
		
				image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
				image = Image.fromarray(image)
				image = ImageTk.PhotoImage(image)
		
				if self.panel is None:
					self.panel = tki.Label(image=image)
					self.panel.image = image
					self.panel.pack(side="left", padx=0, pady=10)
		
				# otherwise, simply update the panel
				else:
					self.panel.configure(image=image)
					self.panel.image = image

		except RuntimeError, e:
			print("[INFO] caught a RuntimeError")

	def takeSnapshot(self):
		# grab the current timestamp and use it to construct the
		# output path
		ts = datetime.datetime.now()
		filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
		p = os.path.sep.join((self.outputPath, filename))

		# save the file
		cv2.imwrite(p, self.frame.copy())
		print("[INFO] saved {}".format(filename))

	def onClose(self):
		# set the stop event, cleanup the camera, and allow the rest of
		# the quit process to continue
		print("[INFO] closing...")
		self.stopEvent.set()
		self.vs.stop()
		self.root.quit()