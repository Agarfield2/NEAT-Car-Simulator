import pygame
import json
import os

class Map:
    def __init__(self, map_file="maps/map.json"):
        """
        Initialise la carte à partir d'un fichier JSON.

        Paramètres :
            map_file : str, optionnel
                Chemin vers le fichier JSON contenant les informations de la carte (par défaut 'map.json').
        """
        # Charge les données de la carte à partir d'un fichier JSON
        with open(map_file, 'r') as f:
            data = json.load(f)

        # Charge l'image de la route
        script_dir = os.path.dirname(__file__)  # dossier où se trouve map.py
        road_image_path = os.path.join(script_dir, "..", "maps", "road.png")
        self.road_surface = pygame.image.load(road_image_path).convert()
        self.road_surface = self.road_surface.convert()

        # Charge les checkpoints
        self.checkpoints = data.get('checkpoints', [])
        # Chaque checkpoint est un dictionnaire avec les clés 'start', 'end', 'order'

        # Charge la position de départ
        self.start_position = data.get('start_position', [100, 100])

        # Crée un masque uniquement pour l'herbe (zones vertes)
        self.grass_mask = self.create_grass_mask()

    def create_grass_mask(self):
        """
        Crée un masque où les zones d'herbe (vertes) sont considérées comme solides.

        Retourne :
            pygame.mask.Mask : Le masque représentant les zones solides de l'herbe.
        """
        # Crée un masque de la même taille que la surface de la route
        grass_mask = pygame.mask.Mask((self.road_surface.get_width(), self.road_surface.get_height()))
        grass_color = (0, 200, 0)  # Couleur de l'herbe (vert)

        # Parcourt chaque pixel de l'image de la route
        for x in range(self.road_surface.get_width()):
            for y in range(self.road_surface.get_height()):
                # Obtient la couleur du pixel actuel
                color = self.road_surface.get_at((x, y))
                # Si la couleur correspond à celle de l'herbe, marque le pixel comme solide dans le masque
                if color[:3] == grass_color:  # Ignore le canal alpha s'il est présent
                    grass_mask.set_at((x, y), 1)  # Marque les zones d'herbe comme solides

        return grass_mask

    def draw(self, screen):
        """
        Dessine la surface de la route sur l'écran.

        Paramètres :
            screen : pygame.Surface
                L'écran sur lequel la surface de la route doit être dessinée.
        """
        screen.blit(self.road_surface, (0, 0))