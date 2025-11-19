import pygame
import sys

from python.car_neat import Car
from python.raycast import Raycast
from python.map import Map
from python.lap_counter import LapCounter

from PIL import Image

# Initialise Pygame
pygame.init()

# Charge l'image de la carte et récupère ses dimensions
map_path = "maps/road.png"
with Image.open(map_path) as map:
    width, height = map.size

# Définition des dimensions de la fenêtre du jeu
WIDTH, HEIGHT = width, height
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Contrôle Manuel de la Voiture")

# Horloge pour contrôler le taux de rafraîchissement
clock = pygame.time.Clock()

# Variables de configuration de la voiture
CAR_WIDTH = 13  # Largeur de la voiture
CAR_HEIGHT = 23  # Hauteur de la voiture
CAR_TURN_SPEED = 150  # Vitesse de rotation de la voiture
CAR_MAX_SPEED = 2000  # Vitesse maximale de la voiture
CAR_MIN_SPEED = 0  # Vitesse minimale de la voiture
CAR_ACCELERATION = 80  # Accélération de la voiture
image_path = "cars/Red_Car.png"  # Chemin vers l'image de la voiture

# Création de l'objet voiture
# Utilise la position de départ de la carte pour initialiser la voiture
game_map = Map()
car = Car(game_map.start_position[0], game_map.start_position[1],
          width=CAR_WIDTH, height=CAR_HEIGHT,
          max_speed=CAR_MAX_SPEED, acceleration=CAR_ACCELERATION,
          turn_speed=CAR_TURN_SPEED, image_path=image_path)

# Variable pour indiquer si le jeu est en cours
running = True

# Boucle principale du jeu
while running:
    # Rafraîchit l'affichage de Pygame
    pygame.display.flip()

    # Dessine l'environnement de jeu
    game_map.draw(screen)

    # Calcul du delta temps réel en utilisant l'horloge
    dt = clock.tick(60) / 1000  # Delta temps en secondes (temps réel)

    # Limite le delta temps pour éviter des sauts trop grands (utile quand les FPS chutent)
    dt = min(dt, 1 / 30)  # Limite dt à un maximum de 1/30 de seconde

    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Si l'utilisateur ferme la fenêtre
            running = False
            pygame.quit()
            sys.exit()

    # Récupère les touches enfoncées
    keys = pygame.key.get_pressed()

    # Logique d'accélération/décélération
    if keys[pygame.K_UP]:
        car.speed += CAR_ACCELERATION * dt  # Accélère la voiture
        car.speed = min(car.speed, CAR_MAX_SPEED)  # Limite la vitesse maximale
    elif keys[pygame.K_DOWN]:
        car.speed -= CAR_ACCELERATION * dt  # Décélère la voiture
        car.speed = max(car.speed, CAR_MIN_SPEED)  # Limite la vitesse minimale

    # Logique de rotation
    if keys[pygame.K_RIGHT] and abs(car.speed) > 0:
        car.angle -= CAR_TURN_SPEED * dt  # Tourne à droite
    elif keys[pygame.K_LEFT] and abs(car.speed) > 0:
        car.angle += CAR_TURN_SPEED * dt  # Tourne à gauche

    # Mise à jour de la voiture avec les nouvelles valeurs
    car.update(dt)

    # Dessine la voiture sur l'écran
    car.draw(screen)

    # Vérifie la collision avec la carte
    if car.check_collision(game_map):
        print("Collision détectée ! Réinitialisation de la position de la voiture.")
        car.reset(game_map.start_position)  # Réinitialise la position de la voiture
        car.speed = 0  # Réinitialise la vitesse à 0

# Point d'entrée du script
if __name__ == "__main__":
    pass