from Recognizer import Recognizer
import Tkinter as tki
import threading
import imutils

class MainView:
	def __init__(self, vs, width=320, height=450):
		self.vs = vs

		self.frame = None
		self.thread = None
		self.stopEvent = None

		self.root = tki.Tk()
		self.root.resizable(width=False, height=False)
		self.root.geometry('{}x{}'.format(width, height))

		self.button = tki.Button(self.root, text="Ring the Bell!", command=self.ring)
		self.button.pack(side="bottom", fill="both", expand="yes", padx=10, pady=10)

		self.stopVideoLoop = threading.Event()
		self.thread = threading.Thread(target=self.videoLoop, args=())
		self.thread.start()

		self.root.wm_title("Hoosthere")
		self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

	def videoLoop(self):
		try:
			a = 0
			while not self.stopVideoLoop.is_set():
				a += 1
		except RuntimeError, e:
			print("[INFO] Runtime Error")
	
	def ring(self):
		return 0

	def onClose(self):
		print("[INFO] Closing")
		self.stopVideoLoop.set()
		self.vs.stop()
		self.root.quit()
		self.root.destroy()