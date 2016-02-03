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
parser.add_argument("-r", "--resolution", action="count", default=0)
parser.add_argument("-s", "--seuil", default=100,
                    help="Fixe la valeur du seuil pour la detection du laser")
parser.add_argument("-f", "--fichier", default=True, type=bool,
                    help="Active l'écriture dans le fichier, par défaut True")
parser.add_argument("-p", "--pas", default=1, type=int,
                    help="nombre de pas. influe sur la precision du scan")
parser.add_argument("--one", action="store_true",
                    help="Active la selection d'un elem par ligne pour le \
                    fichier")
parser.add_argument("-w", "--wait", default=5, type=int,
                    help="Temps entre deux niveaux hauts des bobines du \
                    moteur PaP")
parser.add_argument("--live", action="store_true",
                    help="Activation du flux live reseau")
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
OUVERTURE = 60.0

CONT = 100
SAT = -100
BRI = 75

one_per_line = args.one
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

if sortie_fichier:
    fichier = objets.fichier()


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

    if type(nozero) == tuple and len(nozero[0]) == 0:

        print("[INFO] Aucun point trouve")
        return False, None, None

    """On ne conserve qu'un element par ligne"""
    one_per_line = False

    if one_per_line:
        coord = []
        for k in range(0, len(nozero[1]) - 1):
            if nozero[0][k] != nozero[0][k + 1]:
                # print(k)
                coord.append((nozero[0][k], nozero[1][k]))

        nozero = np.array(coord)

    #print(len(nozero), len(nozero[0]))

    """ renvoit les coordonnees des pixels non noirs, sous forme
    coord[0] = ligne
    coord[1] = colonne
    Reste a convertir en distance reelle  """

    print("[INFO] Point(s) trouve(s)")
    return True, nozero, mask


compteur = 0    # compte le nombre d'image traités
t = []          # Pour stocker les temps    --> pour faire un image/secone


def traitement(bounds):
    """Fonction principale.
    Création du flux vidéo, analyse frame par frame, rotation moteur"""

    global compteur
    global t

    angle = 0
    laser.poweron()

    while angle < 360:
        if compteur != 0:
            # Pour chronometrer le temps de la prise d'une photo
            t = [t[-1]]

        t.append(clock())

        frame = video.read()                # On lit le stream
        frame = frame[0:len(frame), len(frame[0]) / 2:len(frame[0])]

        if affichage > 1:                   # On affiche la frame si demandé
            cv2.imshow("Image", frame)
        # if args.live:
        #    stream.send(frame)

        # on cherche le laser
        etat, coord_laser, masque = recherche_laser(frame, bounds)

        t.append(clock())

        if etat:

            if args.live:
                stream.send(frame)

            if affichage >= 1:
                cv2.imshow("image", masque)
                cv2.waitKey(1)

            # conversion en distance réelles
            profondeur = profondeur_reelle(coord_laser, RESOLUTION, OUVERTURE)
            coord_z = hauteur_reelle(profondeur, coord_laser, RESOLUTION)
            coord_x, coord_y = chgmt_base(profondeur, angle)

            coord_x = coord_x/2
            coord_y = coord_y/2
            coord_z = coord_z/2


            if sortie_fichier:
                fichier.ecriture(coord_x, coord_y, coord_z)

            angle = moteur.step(args.pas, 1)

        compteur += 1

        if angle >= 360:
            laser.poweroff()
            moteur.poweroff()
            return True

try:
    t1 = clock()

    moteur = objets.moteur(args.wait)
    moteur.poweron()
    laser = objets.laser()

    bounds = bound()
    etat = traitement(bounds)


except KeyboardInterrupt:
    print("[INFO] Arret clavier")

finally:
    video.stop()
    t2 = clock()
    laser.poweroff()
    moteur.poweroff()
    fichier.close()
    stream.close()

    for k in range(0, len(t) - 1):

        print(t[k + 1] - t[k])

    print("[END] Nombre d'images traitees %s, en %s secondes" %
          (compteur, t2 - t1))
