def profondeur_reelle(coord_laser, resolution, ouverture):
    x = resolution[0] - coord_laser[1]
    profondeur = ouverture / (1 - x / (resolution[0]))
    return profondeur

def hauteur_reelle(profondeur, coord_laser, resolution):
    tanphi = float(27.6 / 80.5)

    h_au_centre_px = resolution[1]/2 - coord_laser[0]
    hauteur = (profondeur * h_au_centre_px * tanphi) / (resolution[1]/2)

    return hauteur

def chgmt_base(profondeur, angle):
    print("[INFO] Angle courant : ", angle)
    angle = -np.radians(angle)
    liste_x = profondeur * np.cos(angle)
    liste_y = profondeur * np.sin(angle)

    return liste_x, liste_y