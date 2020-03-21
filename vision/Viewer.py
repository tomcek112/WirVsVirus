import cv2
import uuid
import imutils
import numpy as np
from imutils.object_detection import non_max_suppression
from Observation import Observation
import datetime

class Viewer:

    def __init__(self, camera):
        try:
            self.vc = cv2.VideoCapture("http://" + camera.ip + "/mjpg/video.mjpg")
        except(Exception) as error:
            print(error)
        self.camera = camera

    def _captureFrame(self):
        _ret, frame = self.vc.read()
        return frame

    def _countPeople(self, frame):
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector( cv2.HOGDescriptor_getDefaultPeopleDetector() )
        found, w = hog.detectMultiScale(frame, winStride=(4,4), scale=1.03)
        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in found])
        pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)
        return len(pick)

    def createObservation(self):
        if(not self.vc):
            return None
        frame = imutils.resize(self._captureFrame(), width=800)
        val, _w = self._countPeople(frame)
        #self._writeAndClose(val)
        return Observation(uuid.uuid4(), self.camera.id, val, datetime.datetime.now())
