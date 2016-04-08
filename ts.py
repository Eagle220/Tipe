# -*- coding: utf8 -*-
import socket
import cv2
import numpy as np
import struct

host = '192.168.1.67'

#cv2.namedWindow("preview")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, 50000))
        


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    print(msglen)
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        #print(n - len(data))
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

try:
    
    while 1:
        data = recv_msg(s)
        #print(data)
        
        frame = np.fromstring(data, dtype=np.uint8)
        frame = np.reshape(frame, (480,320, 3))
        #print(frame)

        cv2.imshow("prev", frame)
        print("[INFO] Frame reçue \n")
        k = cv2.waitKey(1)
        
except KeyboardInterrupt:
    print('[END] Arret clavier')
except TypeError:
    print("Erreur type")
finally:
    s.close()
    cv2.destroyAllWindows()
