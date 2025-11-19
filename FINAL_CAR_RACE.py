import pygame
import neat
import sys
import os
import pickle
from python.car_neat import Car
from python.raycast import Raycast
from python.map import Map
from python.lap_counter import LapCounter

from PIL import Image

pygame.init()

# Chemin vers l'image de la carte
map_path = "maps/road.png"
with Image.open(map_path) as map:
    width, height = map.size

# Fenêtre de jeu pour la course
WIDTH, HEIGHT = width, height
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Best Cars Race")

clock = pygame.time.Clock()

# Variables de configuration de la voiture
CAR_WIDTH = 13  # Largeur de la voiture
CAR_HEIGHT = 23  # Hauteur de la voiture
CAR_TURN_SPEED = 150  # Vitesse de rotation de la voiture


# Charger les meilleurs résultats des voitures depuis le dossier "final_result"
final_result_dir = "final_result"
car_nets = []  # Liste des réseaux de neurones associés aux voitures
car_names = []  # Liste des noms des voitures

# Charger les réseaux de neurones et paramètres des voitures depuis le dossier "final_result"
for file in os.listdir(final_result_dir):
    if file.endswith(".pkl"):
        car_name = file[:-4]
        # Charger les paramètres de la voiture
        param_file = os.path.join(final_result_dir, f"parameters-{car_name}.txt")
        with open(param_file, "r") as pf:
            params = pf.readlines()
            car_max_speed = float(params[0].strip())  # Vitesse maximale de la voiture
            car_min_speed = float(params[1].strip())  # Vitesse minimale de la voiture
            car_acceleration = float(params[2].strip())  # Accélération de la voiture
            raycast_angles = [float(angle) for angle in params[3].strip().split(",")]  # Angles des rayons pour la détection

        # Charger la configuration NEAT pour chaque voiture
        config_path = os.path.join(final_result_dir, f"config-{car_name}.txt")
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

        # Charger le meilleur génome
        with open(os.path.join(final_result_dir, file), "rb") as f:
            genome = pickle.load(f)
            car_nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
            car_names.append(car_name)

# Initialiser les voitures et les compteurs de tours
game_map = Map()  # Instance de la carte
total_cars = len(car_names)  # Nombre total de voitures
cars = []
raycasts = []
for i, car_name in enumerate(car_names):
    # Charger les paramètres de chaque voiture
    param_file = os.path.join(final_result_dir, f"parameters-{car_name}.txt")
    with open(param_file, "r") as pf:
        params = pf.readlines()
        car_max_speed = float(params[0].strip())
        car_min_speed = float(params[1].strip())
        car_acceleration = float(params[2].strip())
        raycast_angles = [float(angle) for angle in params[3].strip().split(",")]
        print(raycast_angles)
    car = Car(game_map.start_position[0], game_map.start_position[1], width=CAR_WIDTH, height=CAR_HEIGHT,
              max_speed=car_max_speed, acceleration=car_acceleration, turn_speed=CAR_TURN_SPEED, image_path=f"final_result/{car_name}.png")
    cars.append(car)

    raycast=Raycast([float(angle) for angle in params[3].strip().split(",")])
    raycasts.append(raycast)

#raycasts = [Raycast([float(angle) for angle in params[3].strip().split(",")]) for car_name in car_names]
lap_counters = [LapCounter(game_map.checkpoints) for _ in range(total_cars)]

previous_positions = [car.position.copy() for car in cars]  # Positions précédentes des voitures

# Paramètres de la course
running = True
race_complete = False
laps_to_complete = 3  # Nombre de tours à compléter pour terminer la course

# Police d'affichage du tableau des scores
font = pygame.font.Font(None, 24)

# Boucle principale du jeu
while running:
    # Dessiner la carte sur l'écran principal
    screen.fill((0, 0, 0))  # Remplir l'écran de noir
    game_map.draw(screen)  # Dessiner la carte sur l'écran

    dt = clock.tick(60) / 1000  # Temps écoulé en secondes (delta time)
    dt = min(dt, 1 / 30)  # Limiter dt à un maximum de 1/30ème de seconde

    # Gérer les événements utilisateur
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Si l'utilisateur ferme la fenêtre
            running = False
            pygame.quit()
            sys.exit()

    leaderboard = []  # Tableau des scores

    # Mettre à jour chaque voiture
    for i in range(total_cars):
        car = cars[i]
        if not car.active:
            # Dessiner la voiture en gris si elle est inactive
            car_surface = pygame.transform.rotate(pygame.transform.scale(car.surface, (car.width, car.height)), car.angle)
            car_surface.fill((128, 128, 128, 255), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(car_surface, car_surface.get_rect(center=car.position))
        else:
            distances, endpoints = raycasts[i].cast_rays(car.position, car.angle, game_map.road_surface)
            car.draw(screen)  # Dessiner la voiture sur l'écran

            # Normaliser les distances pour le réseau de neurones
            inputs = [distance / 200 for distance in distances]  # Supposant une distance max de 200 pixels
            inputs.append(car.speed / car.max_speed)  # Normaliser la vitesse
            inputs.append(car.angle / 360)  # Normaliser l'angle

            # Entrer les entrées dans le réseau de neurones
            output = car_nets[i].activate(inputs)

            # Logique d'accélération/décélération
            if output[0] > 0.5:
                car.speed += car.acceleration * dt  # Accélérer
            elif output[0] <= 0.5:
                car.speed -= car.acceleration * dt  # Décélérer
                car.speed = max(car.speed, car.min_speed)

            # Logique de rotation
            if output[1] > 0.5 and abs(car.speed) > 0:
                car.angle -= car.turn_speed * dt  # Tourner à droite
            elif output[1] <= 0.5 and abs(car.speed) > 0:
                car.angle += car.turn_speed * dt  # Tourner à gauche

            car.update(dt)  # Mettre à jour la voiture basée sur les nouvelles valeurs

            # Vérifier le passage des points de contrôle
            previous_laps = lap_counters[i].laps_completed
            previous_checkpoints = lap_counters[i].current_checkpoint

            lap_counters[i].check_checkpoint(previous_positions[i], car.position)
            previous_positions[i] = car.position.copy()

            # Si la voiture a complété un tour, mettre à jour son état
            if lap_counters[i].laps_completed > previous_laps:
                if lap_counters[i].laps_completed == laps_to_complete:
                    car.active = False  # Arrêter la voiture après avoir complété les tours requis

            # Détection de collision avec l'herbe (zones hors route) en utilisant la méthode check_collision de la voiture
            if car.check_collision(game_map):
                car.active = False  # Désactiver la voiture si elle touche l'herbe

        # Ajouter la voiture au tableau des scores avec les tours complétés et le point de contrôle actuel
        leaderboard.append((car_names[i], lap_counters[i].laps_completed, lap_counters[i].current_checkpoint, car.active))

    # Trier le tableau des scores : d'abord par tours complétés, puis par points de contrôle
    leaderboard.sort(key=lambda x: (x[1], x[2]), reverse=True)

    # Dessiner le tableau des scores dans le coin supérieur droit
    x_offset = WIDTH - 400
    y_offset = 10
    for rank, (car_name, laps_completed, current_checkpoint, active) in enumerate(leaderboard):
        color = (255, 255, 255) if active else (0, 0, 0)
        text = font.render(f"rank: {rank}, {car_name}: Laps {laps_completed}, Checkpoint {current_checkpoint}", True, color)
        screen.blit(text, (x_offset, y_offset))
        y_offset += 30

    # Mettre à jour l'écran
    pygame.display.flip()