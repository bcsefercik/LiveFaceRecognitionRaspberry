from imutils.video import VideoStream
from View import MainView
import argparse
import time

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--picamera", type=int, default=1,
	help="Use Raspberry Camera")
ap.add_argument("-w", "--width", type=int, default=320,
	help="Witdh of the window")
ap.add_argument("-ht", "--height", type=int, default=450,
	help="Height of the window")
opt = vars(ap.parse_args())

print("[INFO] Launching camera")
vs = VideoStream(usePiCamera=opt["picamera"] > 0).start()
time.sleep(0.4)

view = MainView(vs, width=opt["width"], height=opt["height"])

view.root.mainloop()