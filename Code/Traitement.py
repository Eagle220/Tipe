from threading import Thread
import cv2


class Traitement(object):
    """Classe de traitement des frames"""

    def __init__(self, name, seuil):
        self.name = name
        self.bounds = seuil

    def bound(self.):
    """ on crée les listes des frontieres pour la couleur grise, selon
    les argument fourni. Par défaut à 100 (cf parser)"""

    bound = [
        ([self.seuil, self.args.seuil, self.args.seuil], [255, 255, 255]),
        #       ([10, 31, 4], [220, 255, 255]),
        #       ([25, 146, 190], [62, 174, 250]),
        #       ([103, 86, 65], [145, 133, 128])
    ]
    # on crée les liste up et low si on a plusieurs criteres

    for (low, up) in bound:
        self.low_bound = np.array(low, dtype=np.uint8)
        self.up_bound = np.array(up, dtype=np.uint8)

    def traitement(self):
        mask = cv2.inRange(self.image, self.low_bound, self.up_bound)
        self.frame = frame
        self.nozero = mask.nonzero()

        if type(nozero) == tuple and len(nozero[0]) == 0:
            print("[WARNING] Thread {} : Aucun point trouve".format(self.name))
            self.points_found = False

        else:
            self.points_found = True
            #Debut thread analyse
        print("[INFO] Thread {} : Point(s) trouve(s)".format(self.name))


    def push_frame(self, frame):

    def start(self):
        return
        
