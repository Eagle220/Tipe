#!/usr/bin/env python
# coding:utf8

from picamera import PiCamera
from picamera.array import PiRGBArray
import RPi.GPIO as GPIO

import cv2
import pdb

from fichier import *
from conversionReelle import *
import objets

from time import clock, sleep

import numpy as np
import q
import sys
import argparse

# Créaton du parser pour récupérer et formater les arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-a", "--affichage", action="count", default=0,
    help="Active l'affichage du masque ou frame par frame + masque")
parser.add_argument("-r", "--resolution", action="count", default=0)
parser.add_argument("-s", "--seuil", default=100,
                    help="Fixe la valeur du seuil pour la detection du laser")
parser.add_argument("-f", "--fichier", default=True, type=bool,
                    help="Active l'écriture dans le fichier, par défaut True")
parser.add_argument("-p", "--pas", default=1, type=int,
                    help="nombre de pas par image. influe sur la precision du scan")
args = parser.parse_args()

# -----------------------------------------------------------
# Définition des constantes:

resolution_liste = [
    (640, 480),
    (800, 600),
    (1280, 1024),
    (1920, 1080),
    (2592, 1944)
]

RESOLUTION = resolution_liste[args.resolution]  # choix résolution selon args
OUVERTURE = 45.3

CONT = 100
SAT = -100
BRI = 75

# -----------------------------------------------------------
# Création objet caméra et réglage des paramètres

cam = PiCamera()

# Réglages paramètres caméra

cam.vflip = True                                # On inverse l'image
cam.hflip = True
cam.resolution = RESOLUTION

# Réglage des couleurs selon les paramètres optimaux
cam.saturation = SAT
cam.brightness = BRI
cam.contrast = CONT

affichage = args.affichage
sortie_fichier = args.fichier
# -----------------------------------------------------------

# Fonctions principales :


def bound():
    """ on crée les listes des frontieres pour la couleur grise, selon
    les argument fourni. Par défaut à 100 (cf parser)"""
    bound = [
        ([args.seuil, args.seuil, args.seuil], [255, 255, 255]),
        #       ([10, 31, 4], [220, 255, 255]),
        #       ([25, 146, 190], [62, 174, 250]),
        #       ([103, 86, 65], [145, 133, 128])
    ]
    # on crée les liste up et low si on a plusieurs criteres
    for (low, up) in bound:
        low_bound = np.array(low, dtype='uint8')
        up_bound = np.array(up, dtype='uint8')

    return [low_bound, up_bound]


def recherche_laser(image, bounds):
    """ retourne une matrice contenant les coordonnées hauteur, largeur
     du laser.
     Un seul point par ligne de pixel"""

    # Recuperer matrice avec un seul param par pixel
    mask = cv2.inRange(image, bounds[0], bounds[1])

    """Pour supprimer le bruit : utile mais peu poser probleme quand le laser
    est loin"""
    # mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, None)
    # mask = cv2.erode(mask, None, iterations=1)
    # mask = cv2.dilate(mask, None, iterations=1)

    nozero = mask.nonzero()

    coord = []

    """On ne conserve qu'un element par ligne"""
    for k in range(0, len(nozero[1]) - 1):
        if nozero[0][k] != nozero[0][k + 1]:
            # print(k)
            coord.append((nozero[0][k], nozero[1][k]))

    coord = np.array(coord)
    print(len(coord), len(nozero[0]))

    if coord.any():
        """ renvoit les coordonnees des pixels non noirs, sous forme
        coord[0] = ligne
        coord[1] = colonne
        Reste a convertir en distance reelle  """

        return True, coord, mask
    else:

        print("le masque n'a pas trouve de coordonnes")
        return False, None, None

compteur = 0    # compte le nombre d'image traités
t = []          # Pour stocker les temps    --> pour faire un image/secone


def traitement(cam, bounds):
    """Fonction principale. 
    Création du flux vidéo, analyse frame par frame, rotation moteur"""

    global compteur
    global t

    angle = 0
    laser.allumer()

    if sortie_fichier:
        fichier = ouverture_fichier()

    raw = PiRGBArray(cam)           # Init. récupération image brute

    for f in cam.capture_continuous(raw, format="bgr", use_video_port=True):

        if compteur != 0:
            # Pour choronometrer le temps de la prise d'une photo
            t = [t[-1]]

        t.append(clock())

        frame = f.array         # Conversion en array

        if affichage > 1:                   # On affiche la frame si demandé
            cv2.imshow("Image", frame)

        t.append(clock())

        # on prend que la moitié droite
        frame = frame[0:len(frame), len(frame[0]) / 2:len(frame[0])]
        t.append(clock())

        # on cherche le laser
        etat, coord_laser, masque = recherche_laser(frame, bounds)
        t.append(clock())

        if etat:

            if affichage >= 1:
                cv2.imshow("image", masque)
                cv2.waitKey(1)

            # conversion en distance réelles
            profondeur = profondeur_reelle(coord_laser, RESOLUTION, OUVERTURE)
            coord_z = hauteur_reelle(profondeur, coord_laser, RESOLUTION)
            coord_x, coord_y = chgmt_base(profondeur, angle)

            if sortie_fichier:
                ecriture_fichier(fichier, coord_x, coord_y, coord_z)

            angle = moteur.step(args.pas)

        raw.truncate(0)                 # on vide le buffer pour continuer
        compteur += 1

        if angle >= 360:
            laser.eteindre()
            moteur.poweroff()
            return True

try:
    t1 = clock()
    moteur = objets.moteur()
    moteur.poweron()
    laser = objets.laser()

    bounds = bound()
    etat = traitement(cam, bounds)


except KeyboardInterrupt:
    t2 = clock()
    laser.eteindre()
    moteur.poweroff()
    for k in range(0, len(t) - 1):

        print(t[k + 1] - t[k])

    print("arret clavier ", compteur, t2 - t1)
