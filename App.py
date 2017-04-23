from imutils.video import VideoStream
from View import MainView
import argparse
import time

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="whether or not the Raspberry Pi camera should be used")
opt = vars(ap.parse_args())

print("[INFO] Launching camera")
vs = VideoStream(usePiCamera=opt["picamera"] > 0).start()
time.sleep(2)

view = MainView(vs)

view.root.mainloop()