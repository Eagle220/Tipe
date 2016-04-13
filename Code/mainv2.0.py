# coding:utf8
#!/usr/bin/env python3



import cv2
from time import clock, sleep
import numpy as np
import argparse
from sys import stdout
# import RPi.GPIO as GPIO

from fichier import *
from conversion import *
import objets
from videostream import *
from livestream import *


# Créaton du parser pour récupérer et formater les arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "-a", "--affichage", action="count", default=0,
    help="Active l'affichage du masque ou frame par frame + masque")

parser.add_argument("-s", "--seuil", default=100, type=str,
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
                    0 = 70cm (défaut), 1 = 50cm")
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
    (1296, 972),
    (2592, 1944),

]

ouverture_liste = [70, 50]


# RESOLUTION = resolution_liste[args.resolution]  # choix résolution selon args
RESOLUTION = resolution_liste[args.resolution]
OUVERTURE = ouverture_liste[args.distance]
SEUIL = args.seuil
RAPPORT = args.rapport
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




# -----------------------------------------------------------

# Fonctions principales :


def bound():
    """ on crée les listes des frontieres pour la couleur grise, selon
    les argument fourni. Par défaut à 100 (cf parser)"""
    bound = [
        ([SEUIL, SEUIL, SEUIL], [255, 255, 255]),
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
    return (a, b)


def cleaning(img):
    """clean the picture, applicating erosion and dilatation"""
    mask = cv2.erode(img, None, iterations=1)
    # ask = cv2.dilate(img, None, iterations=1)
    # ou

    return mask


def compute_line(image, bounds):
    """Find the laser line"""

    mask = cv2.inRange(image, bounds[0], bounds[1])

    mask = cleaning(mask)

    nozero = np.nonzero(mask)

    if type(nozero) == tuple and len(nozero[0]) == 0:

        #print("[INFO] Aucun point trouve")
        return False, None

    if args.cleaning > 1:
        nozero = one_per_line(nozero)
    """On ne conserve qu'un element par ligne"""

    """ renvoit les coordonnees des pixels non noirs, sous forme
    coord[0] = ligne
    coord[1] = colonne
    Reste a convertir en distance reelle  """

    #print("[INFO] Point(s) trouve(s)")
    return True, nozero


def traitement(bounds):
    """
    Création du flux vidéo, analyse frame par frame, rotation moteur"""
    global compteur
    compteur = 0
    angle = 0
    angle_str = "[INFO] Angle courant :   "

    print(angle_str)


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

            angle_a_afficher = str(round(angle, 3))
            print(angle_a_afficher)
            stdout(angle_a_afficher)
#
            stdout("\b"*len(angle_a_afficher))

            compteur += 1
try:
    print("[START]          Scanner 3D")
    print("Resolution : ", RESOLUTION)
    print("Distance Laser-Cam", OUVERTURE)
    print("Rapport reduction : 1/", RAPPORT)
    print("Seuil : ", SEUIL)
    
    t1 = clock()
    fichier = objets.fichier(sortie_fichier)
    moteur = objets.moteur(args.wait, RAPPORT)
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
