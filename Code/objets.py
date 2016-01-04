# !/cv/bin/python

import time
import RPi.GPIO as GPIO
import numpy as np
import os


class moteur(object):

    """Objet moteur, pour le moteur pap"""

    def __init__(self, wait=5):

        GPIO.setmode(GPIO.BCM)
        self.motorpin = 21
        self.etat = False
        GPIO.setup(self.motorpin, GPIO.OUT)
        self.StepPins = [27, 22, 23, 24]
        self.position = 0
        self.wait = wait
        self.Seq = [[1, 0, 0, 1],
                    [1, 0, 0, 0],
                    [1, 1, 0, 0],
                    [0, 1, 0, 0],
                    [0, 1, 1, 0],
                    [0, 0, 1, 0],
                    [0, 0, 1, 1],
                    [0, 0, 0, 1]]

        self.StepCount = len(self.Seq)
        for pin in self.StepPins:
            print("Setup pins")
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, False)

    def poweron(self):
        """Alimente le moteur"""
        self.etat = True
        GPIO.output(self.motorpin, self.etat)

    def poweroff(self):
        """ Coupe l'alimentation du moteur (évite la chauffe)"""
        self.etat = False
        GPIO.output(self.motorpin, self.etat)

    def step(self, pas):
        """ Fait un pas, soit 360/512 °"""
        self.StepCounter = 0
# Set to 1 or 2 for clockwise
# Set to -1 or -2 for anti-clockwise

        StepDir = 1
        WaitTime = self.wait / float(1000)

        for k in range(0, 8 * pas):
            for pin in range(0, 4):
                xpin = self.StepPins[pin]

                if self.Seq[self.StepCounter][pin] != 0:

                    GPIO.output(xpin, True)
                else:
                    GPIO.output(xpin, False)

            self.StepCounter += StepDir
            if (self.StepCounter >= self.StepCount):
                self.StepCounter = 0
            if (self.StepCounter < 0):
                self.StepCounter = self.StepCount + StepDir
            time.sleep(WaitTime)
        self.position += 1

        return self.position * 360 / 512


class laser(object):

    """Objet laser, pour le controler"""

    def __init__(self):
        self.etat = False
        self.pin = 17
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, self.etat)

    def poweron(self):
        self.etat = True
        GPIO.output(self.pin, self.etat)

    def poweroff(self):
        self.etat = False
        GPIO.output(self.pin, self.etat)


class fichier(object):

    def __init__(self):
        """ Crée et ouvre un fichier avec un nom unique (date et heure)"""
        self.path = os.getcwd()
        self.nom_fichier = self.path + '/Modelisation/blender ' + \
            time.ctime().replace(':', '-') + '.obj'
        self.fichier = open(self.nom_fichier, "wb")
        self.fichier.write(b"mtllib test.mtl\nv ")

        print("[INFO] Fichier .obj stocké ici : ", self.nom_fichier)

    def ecriture(self, x, y, z):
        """ Écris dans le fichier les données"""
        coord_cart = np.column_stack(
            (x, y, z))           # on cree mat ou chq line = [x,y,z]
        np.savetxt(
            self.nom_fichier, coord_cart, delimiter=" ", newline='\nv ', fmt='%s')

        return True

    def close(self):
        self.fichier.close()


if __name__ == '__main__':
    import sys
    moteur = moteur()
    print("pouet")

    if len(sys.argv) > 1:
        nb_step = int(sys.argv[1])
    else:
        nb_step = 1

    for k in range(512):
        moteur.step(nb_step)
