"""
	Bugra Can Sefercik
	ELEC 491 Term Project
	Face Recognizer Class
	21 April 2017
"""

from imutils.video import VideoStream
import os
import numpy as np
import imutils
import time
import cv2

class Recognizer:
	def __init__(self, model):
		self.model = model
