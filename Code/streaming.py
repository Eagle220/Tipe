import cv2
from videostream import *
import struct

import socket

host = ''
port = 50000
b = 5
s = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.bind((host, port))
s.listen(5)
vs = VideoStream((640, 480), 100, -100, 75, 32).start()
client, address = s.accept()

try:
    while 1:

        f = vs.read()

        frame = f.flatten()
        data = f.tostring()
        msg = struct.pack('>I', len(data)) + data
        print('[INFO] Frame envoyee')

except KeyboardInterrupt:
    print("\n[END] Arret clavier")

finally:
    s.close()
    vs.stop()
    
