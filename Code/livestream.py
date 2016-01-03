

import cv2
import struct

import socket


class LiveStream(object):

    def __init__(self):
        """Initialisation"""
        self.host = ''
        self.port = 50000
        self.b = 5
        

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

    def close(self):
        """ Ferme la connexion"""
        self.s.close()
