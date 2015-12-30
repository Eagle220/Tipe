#!/usr/bin/env python
# coding:utf8

from picamera import PiCamera
from picamera.array import PiRGBArray
from threading import Thread


class VideoStream(object):

    def __init__(self, resolution, contrast, saturation, brightness, fps=32):
        self.cam = PiCamera()
        self.cam.resolution = resolution
        self.cam.contrast = contrast
        self.cam.saturation = saturation
        self.cam.brightness = brightness

        self.cam.hflip = True
        self.cam.vflip = True

        self.rawCapture = PiRGBArray(self.cam, size=resolution)
        self.stream = self.cam.capture_continuous(
            self.rawCapture, format="bgr", use_video_port=True)

        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)
            # if the thread indicator variable is set, stop the thread
            # and resource cam resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.cam.close()
                return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
