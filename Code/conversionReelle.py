# coding:utf8
#!/usr/bin/env python3

import numpy as np
import pdb


def profondeur_reelle(coord_laser, resolution, ouverture):
    """
    calcule la profondeur reelle entre le capteur et l'objet en fonction de:
    - coord_laser (np.array) : matrice des coordonnee des pixels non noirs,
        sous forme x,y
          On travaille uniquement avec x --> coord_laser[1]
    - resolution (tuple) : resolution appareil
          On a juste besoin de la largeur --> resolution[0]
    - ouverture = distance mini pour voir un objet
    retourne une array
    """

    # Pour avoir la distance depuis le bord droit
    # pdb.set_trace()
    x = resolution[0] - coord_laser[1]
    profondeur = ouverture / (1 - x / (resolution[0] / 2))
    return - profondeur


def hauteur_reelle(profondeur, coord_laser, resolution):
    """ calcule la hauteur reelle d'un point detecté par le laser en fonction de:
    - profondeur (np.array) : resultat de profondeur_reelle
    - coord_laser (np.array) : matrice des coordonnee des pixels non noirs,
        sous forme x,y
          On travaille uniquement avec y --> coord_laser[0]
    - resolution (tuple) : resolution appareil
          On a juste besoin de la hauteur --> resolution[1]"""

    tanphi = float(27.6 / 80.5)

    h_au_centre_px = resolution[1] - coord_laser[0]
    hauteur = (profondeur * h_au_centre_px * tanphi) / resolution[1]
    return hauteur


def chgmt_base(profondeur, angle):
    """On passe en coordonnées cartesiennes, grace a
    - profondeur (np.array) : resultat de profondeur_reelle
    - angle (scalaire) : position angulaire dispositif donnée par moteur pap"""
    angle = np.radians(angle)
    liste_x = profondeur * np.cos(angle)
    liste_y = profondeur * np.sin(angle)

    return liste_x, liste_y
