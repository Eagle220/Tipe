# coding:utf8

import cv2
import struct

import socket


class LiveStream(object):

    def __init__(self):
        """Initialisation"""
        self.host = ''
        self.port = 50000
        self.b = 5
        self.state = False

    def send(self, f):
        """ Envoie un image"""
#        self.f = cv2.cvtColor(self.f, cv2.COLOR_BGR2GRAY)
    #        print(f)
    #        frame = f.flatten()
        self.data = f.tostring()
    #        print(len(data))
        self.msg = struct.pack('>I', len(self.data)) + self.data
        print('[INFO] Frame envoyee')
        self.client.sendall(self.msg)

    def open(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        """Ouvre le socket pour la visualisation live"""
        self.s.bind((self.host, self.port))
        self.s.listen(5)
        self.client, self.address = self.s.accept()
        print("[INFO] Client connecte depuis ", self.address)

        self.state = True

    def close(self):
        """ Ferme la connexion"""
        if self.state:
            self.s.close()
            self.state = False

if __name__ == '__main__':

    print("Test Livestream")
    from videostream import *
    import time

    vs = VideoStream().start()

    stream = LiveStream()
    stream.open()
    time.sleep(1.0)

    try:
        while True:
            f = vs.read()
            while f is None:
                f = vs.read()
                print("None")
            stream.send(f)

    except KeyboardInterrupt:
        print("[INFO] Arret clavier")
    finally:
        vs.stop()
        stream.close()
