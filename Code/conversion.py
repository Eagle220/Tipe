# coding:utf8

import numpy as np


def profondeur_reelle(coord_laser, resolution, ouverture):
    """
    Calcule la distance entre le scanner et les objets detectes.
    Utilise uniquement les num de colonnes de l'image (=coord_laser[1])
    """

    x = resolution[0] - coord_laser[1]      # On place l'origine a droite
    profondeur = ouverture / (1 - x / (resolution[0]))
    return profondeur


def hauteur_reelle(profondeur, coord_laser, resolution):
    """
    Calcule la hauteur reelle des objets scannees.
    Utilise uniquement les num de ligne de l'image (=coord_laser[0])
    """
    
    tanphi = float(27.6 / 80.5)             # cone d'ouverture vertical camera

    h_au_centre_px = resolution[1] / 2 - coord_laser[0]   # Origine au milieu
    hauteur = (profondeur * h_au_centre_px * tanphi) / (resolution[1] / 2)

    return hauteur


def chgmt_base(profondeur, angle):
    """
    Passage en coordonnes cartésiennes
    """
    print("[INFO] Angle courant : ", angle)
    angle = -np.radians(angle)
    liste_x = profondeur * np.cos(angle)
    liste_y = profondeur * np.sin(angle)

    return liste_x, liste_y
