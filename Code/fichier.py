#!/cv/bin/python
# coding:utf8
import time
import numpy as np
import pdb
import os


def ouverture_fichier():
    """ Crée et ouvre un fihcier avec un nom unique (date et heure)"""
    path = os.path.curdir
    nom_fichier = path + '\\blender ' + time.ctime().replace(':', '-') + '.obj'
    fichier = open(nom_fichier, "wb")
    fichier.write(b"mtllib test.mtl\nv ")
    return fichier


def ecriture_fichier(fichier, x, y, z):
    """ Écris dans le fichier les données"""
    coord_cart = np.column_stack(
        (x, y, z))           # on cree mat ou chq line = [x,y,z]

    #pdb.set_trace()
    np.savetxt(fichier, coord_cart, delimiter=" ", newline='\nv ', fmt='%s')

    return True
