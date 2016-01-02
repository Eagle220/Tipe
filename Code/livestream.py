

import cv2
import struct

import socket


class LiveStream(object):

    def __init__(self):

        self.host = ''
        self.port = 50000
        self.b = 5
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.s.bind((self.host, self.port))
        self.s.listen(5)

        self.client, self.address = self.s.accept()

    def send(self, f):

#        self.f = cv2.cvtColor(self.f, cv2.COLOR_BGR2GRAY)
    #        print(f)
    #        frame = f.flatten()
        self.data = self.f.tostring()
    #        print(len(data))
        self.msg = struct.pack('>I', len(self.data)) + self.data
        print('[INFO] Frame envoyee')
        self.client.sendall(self.msg)

    def close(self):
        self.s.close()

#if __name__ == '__main__':
#    try:
#
#
#
#    except KeyboardInterrupt:
#        print("\n[END] Arret clavier")
#x
#    finally:
#        s.close()
#        vs.stop()
