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

        self.raw = PiRGBArray(self.cam, size=self.resolution)
        self.stream = self.cam.capture_continuous(
            self.raw, format="bgr", use_vide_port=True)

        self.frame = None
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        for f in self.stream:
            self.frame = f.array
            # On ne prends que la moitie
            self.frame = self.frame[
                0:len(self.frame), len(self.frame[0]) / 2:len(self.frame[0])]
            self.raw.truncate(0)

            if self.stopped:
                self.stream.close()
                self.raw.close()
                self.cam.close()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
