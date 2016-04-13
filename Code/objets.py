# coding:utf8
# !/cv/bin/python

import time
import RPi.GPIO as GPIO
import numpy as np
import os


class moteur(object):

    """Objet moteur, pour le moteur pap"""

    def __init__(self, wait, rapport):

        GPIO.setmode(GPIO.BCM)
        self.motorpin = 21
        self.etat = False
        GPIO.setup(self.motorpin, GPIO.OUT)
        self.StepPins = [27, 22, 23, 24]
        self.position = 0
        self.wait = wait
        self.rapport = rapport
        print(self.rapport)
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
        GPIO.cleanup()

    def step(self, pas, StepDir):
        """ Fait un pas, soit 360/512 °"""
        self.StepCounter = 0
# Set to 1 or 2 for clockwise
# Set to -1 or -2 for anti-clockwise

#        StepDir = 1
        WaitTime = self.wait / float(1000)

        for k in range(0,  8 * pas):
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
        print(self.position)

        print(self.position * (360 / 512) * (1 / self.rapport))
        return self.position * (360 / 512) * (1 / self.rapport)


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

    def __init__(self, filename):
        """ Crée et ouvre un fichier avec un nom unique (date et heure)"""
        self.path = os.getcwd()
        if filename == 'None':
            t = time.localtime()

            date = "{}-{}-{}--{}-{}".format(t[2], t[1], t[0], t[3], t[4])
            self.nom_fichier = self.path + \
                '/Modelisation/Scan_' + date + '.obj'

        else:
            self.nom_fichier = str(filename).rstrip('.txt') + '.txt'

        self.fichier = open(self.nom_fichier, "wb")
        self.opened = True
        self.fichier.write(b"mtllib test.mtl\nv ")

        print("[INFO] Fichier .obj stocké ici : ", self.nom_fichier)

    def ecriture(self, x, y, z):
        """ Écris dans le fichier les données"""
        coord_cart = np.column_stack((x, y, z))
        np.savetxt(
            self.fichier, coord_cart, delimiter=" ", newline='\nv ', fmt='%s')

        return True

    def efface_derniere_ligne(self):
        if self.opened:
            self.close(self)
        from os import popen
        popen("sed '$d' -i " + self.nom_fichier)

    def close(self):
        self.opened = False
        self.fichier.close()
        self.efface_derniere_ligne()


if __name__ == '__main__':

    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pas", default=1, type=int,
                        help="nombre de pas")
    parser.add_argument("-s", "--sens", default=1, type=int,
                        help="Sens de rotation")
    parser.add_argument("-r", "--rapport", default=1, type=int,
                        help="Modifie la precision angulaire")
    parser.add_argument("-t", "--waittime", default=5,
                        help="Temps entre deux niveau haut bobine")
    args = parser.parse_args()
    moteur = moteur(int(args.waittime), int(args.rapport))
    print("[INFO] Démarrage du moteur")

    try:
        while True:
            angle = moteur.step(args.pas, args.sens)
            #print(angle)
    except KeyboardInterrupt:
        print("[END] Fin")
