import pygame
import sys
import json
import os

# Initialise Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 1400, 700  # Dimensions de la fenêtre
MAP_FILE = "maps/map.json"  # Fichier de la carte
ROAD_COLOR = (128, 128, 128)  # Couleur des routes (gris)
GRASS_COLOR = (0, 200, 0)  # Couleur de l'herbe (vert)
CHECKPOINT_COLOR = (255, 255, 0)  # Couleur des checkpoints (jaune)
START_COLOR = (0, 0, 255)  # Couleur de la position de départ (bleu)
BRUSH_COLOR = ROAD_COLOR  # Couleur actuelle du pinceau
BRUSH_SIZE = 30  # Taille initiale du pinceau
CHECKPOINT_LINE_WIDTH = 3  # Épaisseur des lignes des checkpoints
CHECKPOINT_FONT_SIZE = 20  # Taille de la police pour les numéros des checkpoints

# Configuration de l'écran
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Éditeur de Carte de Jeu de Course")
clock = pygame.time.Clock()

# Polices
font = pygame.font.SysFont(None, CHECKPOINT_FONT_SIZE)

# Modes
MODE_DRAW = 'draw'
MODE_CHECKPOINT = 'checkpoint'
MODE_START = 'start'

class MapEditor:
    def __init__(self):
        """
        Initialise l'éditeur de carte.
        """
        # Initialise la surface de la route avec de l'herbe
        self.road_surface = pygame.Surface((WIDTH, HEIGHT))
        self.road_surface.fill(GRASS_COLOR)

        # Initialise la surface de la carte
        self.map_surface = pygame.Surface((WIDTH, HEIGHT))
        self.map_surface.fill(GRASS_COLOR)

        # Structures de données pour les checkpoints et la position de départ
        self.checkpoints = []  # Liste des dictionnaires : {'start': (x, y), 'end': (x, y), 'order': int}
        self.start_position = None  # Tuple (x, y) pour la position de départ

        # Mode actuel
        self.mode = MODE_DRAW

        # Paramètres du pinceau
        self.brush_size = BRUSH_SIZE
        self.brush_color = BRUSH_COLOR

        # État du dessin de checkpoint
        self.drawing_checkpoint = False
        self.checkpoint_start = None
        self.next_checkpoint_order = 1  # Numéro d'ordre pour les checkpoints

    def draw_brush(self, pos, color):
        """
        Dessine un cercle sur la surface de la route pour simuler l'action du pinceau.

        Paramètres :
            pos : tuple (int, int)
                Position (x, y) du pinceau.
            color : tuple (int, int, int)
                Couleur à dessiner.
        """
        pygame.draw.circle(self.road_surface, color, pos, self.brush_size)

    def start_checkpoint_drawing(self, pos):
        """
        Démarre le dessin d'une ligne de checkpoint.

        Paramètres :
            pos : tuple (int, int)
                Position (x, y) de départ du checkpoint.
        """
        self.drawing_checkpoint = True
        self.checkpoint_start = pos

    def finish_checkpoint_drawing(self, pos):
        """
        Termine le dessin d'une ligne de checkpoint et l'enregistre avec un numéro d'ordre.

        Paramètres :
            pos : tuple (int, int)
                Position (x, y) de fin du checkpoint.
        """
        if self.drawing_checkpoint and self.checkpoint_start:
            checkpoint = {
                'start': self.checkpoint_start,
                'end': pos,
                'order': self.next_checkpoint_order
            }
            self.checkpoints.append(checkpoint)
            self.next_checkpoint_order += 1
            self.drawing_checkpoint = False
            self.checkpoint_start = None
            print(f"Checkpoint {checkpoint['order']} placé de {checkpoint['start']} à {checkpoint['end']}.")

    def delete_last_checkpoint(self):
        """
        Supprime le dernier checkpoint s'il en existe un.
        """
        if self.checkpoints:
            removed_checkpoint = self.checkpoints.pop()
            self.next_checkpoint_order -= 1
            print(f"Checkpoint {removed_checkpoint['order']} supprimé de {removed_checkpoint['start']} à {removed_checkpoint['end']}.")
        else:
            print("Aucun checkpoint à supprimer.")

    def render_checkpoint(self, checkpoint):
        """
        Dessine un checkpoint avec son numéro d'ordre.

        Paramètres :
            checkpoint : dict
                Dictionnaire contenant les informations du checkpoint ('start', 'end', 'order').
        """
        start = checkpoint['start']
        end = checkpoint['end']
        order = checkpoint['order']
        pygame.draw.line(self.map_surface, CHECKPOINT_COLOR, start, end, CHECKPOINT_LINE_WIDTH)
        midpoint = ((start[0] + end[0]) // 2, (start[1] + end[1]) // 2)
        order_text = font.render(str(order), True, (255, 255, 255))
        text_rect = order_text.get_rect(center=midpoint)
        self.map_surface.blit(order_text, text_rect)

    def render_all_checkpoints(self):
        """
        Dessine tous les checkpoints de la liste des checkpoints.
        """
        for checkpoint in self.checkpoints:
            self.render_checkpoint(checkpoint)

    def set_start_position(self, pos):
        """
        Définit la position de départ du joueur.

        Paramètres :
            pos : tuple (int, int)
                Position (x, y) de départ.
        """
        self.start_position = pos
        print(f"Position de départ définie à {pos}.")

    def render_start_position(self):
        """
        Dessine la position de départ sur la surface de la carte.
        """
        if self.start_position:
            pygame.draw.circle(self.map_surface, START_COLOR, self.start_position, 8, 2)
            start_text = font.render("Départ", True, (255, 255, 255))
            text_rect = start_text.get_rect(center=(self.start_position[0], self.start_position[1] - 15))
            self.map_surface.blit(start_text, text_rect)

    def save_map(self):
        """
        Sauvegarde la carte actuelle dans 'maps/road.png' et 'maps/map.json'.
        """
        data = {
            'checkpoints': self.checkpoints,
            'start_position': self.start_position
        }
        pygame.image.save(self.road_surface, "maps/road.png")
        data['road_image'] = "maps/road.png"
        with open(MAP_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        print("Carte sauvegardée avec succès.")

    def load_map(self):
        """
        Charge la carte depuis 'maps/road.png' et 'maps/map.json'.
        """
        if not os.path.exists(MAP_FILE):
            print("Aucun fichier de carte trouvé à charger.")
            return
        with open(MAP_FILE, 'r') as f:
            data = json.load(f)

        road_image_path = data.get('road_image')
        if road_image_path and os.path.exists(road_image_path):
            road_image = pygame.image.load(road_image_path).convert()
            self.road_surface.blit(road_image, (0, 0))
        else:
            self.road_surface.fill(GRASS_COLOR)

        self.map_surface.fill(GRASS_COLOR)
        self.map_surface.blit(self.road_surface, (0, 0))

        self.checkpoints = data.get('checkpoints', [])
        self.next_checkpoint_order = len(self.checkpoints) + 1
        self.render_all_checkpoints()

        self.start_position = data.get('start_position')
        if self.start_position:
            self.render_start_position()

        print("Carte chargée avec succès.")

    def handle_event(self, event):
        """
        Gère les événements Pygame entrants.

        Paramètres :
            event : pygame.event.Event
                Événement Pygame à gérer.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if self.mode == MODE_DRAW:
                if event.button == 1:  # Clic gauche pour dessiner les routes
                    self.draw_brush(pos, ROAD_COLOR)
                elif event.button == 3:  # Clic droit pour effacer (dessiner de l'herbe)
                    self.draw_brush(pos, GRASS_COLOR)
            elif self.mode == MODE_CHECKPOINT:
                if event.button == 1:  # Clic gauche pour commencer à dessiner un checkpoint
                    self.start_checkpoint_drawing(pos)
                elif event.button == 3:  # Clic droit pour supprimer le dernier checkpoint
                    self.delete_last_checkpoint()
            elif self.mode == MODE_START:
                if event.button == 1:  # Clic gauche pour définir la position de départ
                    self.set_start_position(pos)

        elif event.type == pygame.MOUSEBUTTONUP:
            pos = pygame.mouse.get_pos()
            if self.mode == MODE_CHECKPOINT:
                if event.button == 1 and self.drawing_checkpoint:
                    self.finish_checkpoint_drawing(pos)

        elif event.type == pygame.MOUSEMOTION:
            pos = pygame.mouse.get_pos()
            if self.mode == MODE_DRAW:
                if pygame.mouse.get_pressed()[0]:
                    self.draw_brush(pos, ROAD_COLOR)
                elif pygame.mouse.get_pressed()[2]:
                    self.draw_brush(pos, GRASS_COLOR)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.mode = MODE_DRAW
                print("Mode Dessin activé.")
            elif event.key == pygame.K_2:
                self.mode = MODE_CHECKPOINT
                print("Mode Checkpoint activé.")
            elif event.key == pygame.K_3:
                self.mode = MODE_START
                print("Mode Position de Départ activé.")
            elif event.key in [pygame.K_EQUALS, pygame.K_PLUS]:
                self.brush_size += 1
                print(f"Taille du pinceau augmentée à {self.brush_size}")
            elif event.key in [pygame.K_MINUS, pygame.K_RIGHTPAREN]:
                self.brush_size = max(1, self.brush_size - 1)
                print(f"Taille du pinceau diminuée à {self.brush_size}")
            elif event.key == pygame.K_s:
                self.save_map()
            elif event.key == pygame.K_l:
                self.load_map()

    def render(self, surface):
        """
        Rend la carte et l'interface utilisateur sur la surface donnée.

        Paramètres :
            surface : pygame.Surface
                Surface sur laquelle la carte et l'interface utilisateur doivent être dessinées.
        """
        self.map_surface.fill(GRASS_COLOR)
        self.map_surface.blit(self.road_surface, (0, 0))
        self.render_all_checkpoints()
        if self.start_position:
            self.render_start_position()
        surface.blit(self.map_surface, (0, 0))
        if self.mode == MODE_DRAW:
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(surface, (255, 255, 255), mouse_pos, self.brush_size, 1)
        self.display_ui(surface)

    def display_ui(self, surface):
        """
        Affiche les éléments de l'interface utilisateur.

        Paramètres :
            surface : pygame.Surface
                Surface sur laquelle les éléments de l'interface utilisateur doivent être affichés.
        """
        mode_text = f"Mode : {self.mode.capitalize()}"
        img = font.render(mode_text, True, (255, 255, 255))
        surface.blit(img, (10, HEIGHT - 200))

        brush_text = f"Taille du pinceau : {self.brush_size}"
        img = font.render(brush_text, True, (255, 255, 255))
        surface.blit(img, (10, HEIGHT - 180))

        instructions = [
            "1 : Dessiner des routes",
            "2 : Placer des checkpoints",
            "3 : Définir la position de départ",
            "S : Sauvegarder la carte",
            "L : Charger la carte",
            "+/- : Augmenter/Diminuer la taille du pinceau",
            "Clic gauche : Action selon le mode",
            "Clic droit (Mode Dessin) : Effacer (Dessiner de l'herbe)",
            "Clic droit (Mode Checkpoint) : Supprimer le dernier checkpoint"
        ]
        for i, text in enumerate(instructions):
            img = font.render(text, True, (255, 255, 255))
            surface.blit(img, (10, HEIGHT - 160 + i * 20))

def main():
    editor = MapEditor()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            editor.handle_event(event)

        editor.render(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()