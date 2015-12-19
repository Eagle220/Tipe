# !/cv/bin/python

import time
import RPi.GPIO as GPIO


class moteur(object):

    """Objet moteur, pour le moteur pap"""

    def __init__(self):

        GPIO.setmode(GPIO.BCM)
        self.motorpin = 21
        self.etat = False
        GPIO.setup(self.motorpin, GPIO.OUT)
        self.StepPins = [27, 22, 23, 24]
        self.position = 0
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
        print(pas)
        self.StepCounter = 0
        StepDir = 1  # Set to 1 or 2 for clockwise
                    # Set to -1 or -2 for anti-clockwise

        WaitTime = 4 / float(1000)

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

    def allumer(self):
        self.etat = True
        GPIO.output(self.pin, self.etat)

    def eteindre(self):
        self.etat = False
        GPIO.output(self.pin, self.etat)


if __name__ == '__main__':
    moteur = moteur()
    print("pouet")

    for k in range(512):
        moteur.step()
