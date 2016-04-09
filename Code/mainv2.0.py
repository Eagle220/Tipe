#!/usr/bin/env python3

# coding:utf8

import cv2

# import RPi.GPIO as GPIO

from fichier import *
from conversion import *
import objets
from videostream import *
from livestream import *

from time import clock, sleep

import numpy as np

import argparse

# Créaton du parser pour récupérer et formater les arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-a", "--affichage", action="count", default=0,
    help="Active l'affichage du masque ou frame par frame + masque")
#parser.add_argument("--resolution", action="count", default=0)
parser.add_argument("-s", "--seuil", default=100,
                    help="Fixe la valeur du seuil pour la detection du laser")
parser.add_argument("-f", "--fichier", default='None', type=str,
                    help="Permet de choisir le nom du fichier")
parser.add_argument("-p", "--pas", default=1, type=int,
                    help="nombre de pas. influe sur la precision du scan")

parser.add_argument("-w", "--wait", default=5, type=int,
                    help="Temps entre deux niveaux hauts des bobines du \
                    moteur PaP")
parser.add_argument("--live", action="store_true",
                    help="Activation du flux live reseau")
parser.add_argument("-r", "--rapport", default=1, type=int,
                    help="Modifie la precision angulaire")
parser.add_argument("-d", "--distance", default=0, type=int,
                    help="Règle la distance entre laser et camera. \
                    0 = 60cm (défaut), 1 = 50cm")
parser.add_argument("--resolution", default=0, type=int,
                    help="choisi la resolution camera. Defaut : 640*480")
parser.add_argument("-c", "--cleaning", action="count", default=0,
                    help="active le nettoyage du masque (plus propre \
                    mais moins de pts)")
args = parser.parse_args()

# -----------------------------------------------------------
# Définition des constantes:

resolution_liste = [
    (640, 480),
    (1280, 960),
    (1280, 1024),
    (1920, 1080),
    (2592, 1944)
]

ouverture_liste = [60, 50]

# RESOLUTION = resolution_liste[args.resolution]  # choix résolution selon args
RESOLUTION = resolution_liste[args.resolution]
OUVERTURE = ouverture_liste[args.distance]

CONT = 100
SAT = -100
BRI = 75


# -----------------------------------------------------------
# Démarrage de flux video et flux live

video = VideoStream(RESOLUTION, CONT, SAT, BRI).start()
sleep(1.0)      # On laisse le tmeps au flux de s'intialiser


print(args.live)
stream = LiveStream()

if args.live:
    stream.open()

# -----------------------------------------------------------
# Definition variable choix affichage
affichage = args.affichage

# -----------------------------------------------------------
# Réglage de la sortie fichier

sortie_fichier = args.fichier

fichier = objets.fichier(sortie_fichier)


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
        low_bound = np.array(low, dtype=np.uint8)
        up_bound = np.array(up, dtype=np.uint8)
    return [low_bound, up_bound]


def one_per_line(nozero):
    """return only one element per line"""
    x = nozero[0]
    y = nozero[1]

    first_occurences_mask = np.concatenate([[1], np.diff(x)], axis=0) > 0
    a, b = (x[first_occurences_mask], y[first_occurences_mask])
    return (a,b)


def cleaning(img):
    """clean the picture, applicating erosion and dilatation"""
    mask = cv2.erode(img, None, iterations=1)
    #mask = cv2.dilate(img, None, iterations=1)
    # ou

    return mask


def compute_line(image, bounds):
    """Find the laser line"""

    mask = cv2.inRange(image, bounds[0], bounds[1])
    if args.cleaning > 0:
        mask = cleaning(mask)

    nozero = np.nonzero(mask)

    if args.cleaning > 1:
        nozero = one_per_line(nozero)
    



    if type(nozero) == tuple and len(nozero[0]) == 0:

        print("[INFO] Aucun point trouve")
        return False, None

    """On ne conserve qu'un element par ligne"""

    #print(len(nozero), len(nozero[0]))

    """ renvoit les coordonnees des pixels non noirs, sous forme
    coord[0] = ligne
    coord[1] = colonne
    Reste a convertir en distance reelle  """

    print("[INFO] Point(s) trouve(s)")
    return True, nozero


def traitement(bounds):
    """
    Création du flux vidéo, analyse frame par frame, rotation moteur"""
    global compteur
    compteur = 0
    angle = 0
    laser.poweron()

    while angle < 360:

        frame = video.read()
        frame = frame[0:len(frame), len(frame[0]) / 2:len(frame[0])]

        # on cherche le laser
        state, coord_laser = compute_line(frame, bounds)

        if state:

            if args.live:
                stream.send(frame)

            # conversion en distance réelles
            profondeur = profondeur_reelle(coord_laser, RESOLUTION, OUVERTURE)
            coord_z = hauteur_reelle(profondeur, coord_laser, RESOLUTION)
            coord_x, coord_y = chgmt_base(profondeur, angle)

            coord_x = coord_x / 2
            coord_y = coord_y / 2
            coord_z = coord_z / 2

            fichier.ecriture(coord_x, coord_y, coord_z)

            angle = moteur.step(args.pas, 1)
            compteur += 1
try:
    t1 = clock()

    moteur = objets.moteur(args.wait, args.rapport)
    moteur.poweron()
    laser = objets.laser()

    bounds = bound()
    etat = traitement(bounds)


except KeyboardInterrupt:
    print("[STOP] Arret clavier")

finally:
    video.stop()
    t2 = clock()
    laser.poweroff()
    moteur.poweroff()
    fichier.close()
    stream.close()

    print("[END] Nombre d'images traitees %s, en %s secondes" %
          (compteur, t2 - t1))
