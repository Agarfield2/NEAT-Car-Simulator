import pygame
import neat
import sys
import os
import pickle




#from FINAL_CAR_RACE import car_min_speed
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
pygame.display.set_caption("Course des Meilleures Voitures")

# Horloge pour contrôler le taux de rafraîchissement
clock = pygame.time.Clock()

# Variables de configuration de la voiture
CAR_WIDTH = 13  # Largeur de la voiture
CAR_HEIGHT = 23  # Hauteur de la voiture
CAR_TURN_SPEED = 150  # Vitesse de rotation de la voiture

# Variables modifiables pour la configuration de la voiture
CAR_MAX_SPEED = 2000  # Vitesse maximale de la voiture
CAR_MIN_SPEED = 0  # Vitesse minimale de la voiture
CAR_ACCELERATION = 80  # Accélération de la voiture
Raycast_angles = [-67.5, -45, -22.5, 0, 22.5, 45, 67.5]  # Angles des rayons pour la détection
image_path = "cars/Blue_F1.png"  # Chemin vers l'image de la voiture
team_name = "Agarfield F1"  # Nom de l'équipe

# Variables pour NEAT
GENERATION = 0  # Génération actuelle


# Charge la configuration de NEAT
def load_config(config_path):
    """
    Charge le fichier de configuration pour NEAT.

    Paramètres :
        config_path : str
            Chemin vers le fichier de configuration.

    Retourne :
        neat.Config : L'objet de configuration chargé.
    """
    return neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

# Exécute l'algorithme NEAT et sauvegarde la meilleure configuration de voiture
def run_neat(config_file, checkpoint_path=None):
    """
    Exécute l'algorithme NEAT et sauvegarde la meilleure configuration de voiture.

    Paramètres :
        config_file : str
            Chemin vers le fichier de configuration.
        checkpoint_path : str, optionnel
            Chemin vers le fichier de checkpoint pour charger la progression précédente.
    """
    global team_name

    if checkpoint_path and os.path.exists(checkpoint_path):
        # Charge la population depuis un checkpoint
        population = neat.Checkpointer.restore_checkpoint(checkpoint_path)
    else:
        # Crée une nouvelle population
        config = load_config(config_file)
        population = neat.Population(config)

    # Ajoute des reporters pour afficher les informations
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Ajoute un Checkpointer pour sauvegarder la progression toutes les 5 générations
    checkpoint_dir = "checkpoint"
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    population.add_reporter(neat.Checkpointer(5, filename_prefix=os.path.join(checkpoint_dir, "neat-checkpoint-")))

    # Exécute l'algorithme NEAT
    winner = population.run(eval_genomes, 2000) # 50 générations

    # Sauvegarde le meilleur génome et sa configuration
    final_result_dir = "final_result"
    if not os.path.exists(final_result_dir):
        os.makedirs(final_result_dir)
    car_name = team_name
    with open(os.path.join(final_result_dir, f"{car_name}.pkl"), "wb") as f:
        pickle.dump(winner, f)
    with open(os.path.join(final_result_dir, f"config-{car_name}.txt"), "w") as f:
        with open(config_file, "r") as config_f:
            f.write(config_f.read())
    with open(os.path.join(final_result_dir, f"parameters-{car_name}.txt"), "w") as f:
        f.write(f"{CAR_MAX_SPEED}\n{CAR_MIN_SPEED}\n{CAR_ACCELERATION}\n{','.join([str(angle) for angle in Raycast_angles])}")

    # Sauvegarde l'image de la voiture
    if image_path:
        with open(os.path.join(final_result_dir, f"{car_name}.png"), "wb") as f:
            with open(image_path, "rb") as img_f:
                f.write(img_f.read())

    print(f"Meilleur génome sauvegardé dans {final_result_dir}/{car_name}.pkl")

# Variable pour afficher ou masquer les rayons
raycast_visible = False

# Fonction d'évaluation des génomes
def eval_genomes(genomes, config):
    """
    Évalue chaque génome dans la population pour déterminer la meilleure voiture.

    Paramètres :
        genomes : list
            Liste des génomes à évaluer.
        config : neat.Config
            Configuration utilisée pour le réseau neuronal.
    """
    global GENERATION, raycast_visible, Raycast_angles, CAR_MAX_SPEED, CAR_MIN_SPEED, CAR_ACCELERATION, image_path
    GENERATION += 1

    nets = []
    ge = []
    cars = []

    # Charge la carte
    game_map = Map()

    for genome_id, genome in genomes:
        genome.fitness = 0  # Fitness initiale
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

        # Crée une nouvelle voiture pour chaque génome
        car = Car(game_map.start_position[0], game_map.start_position[1],
                  width=CAR_WIDTH, height=CAR_HEIGHT,
                  max_speed=CAR_MAX_SPEED, acceleration=CAR_ACCELERATION,
                  turn_speed=CAR_TURN_SPEED, image_path=image_path, min_speed=CAR_MIN_SPEED)
        cars.append(car)
        ge.append(genome)

    # Crée l'objet Raycast avec des angles personnalisés
    angles = Raycast_angles  # Angles modulables des rayons
    raycast = Raycast(angles)

    # Compteur de tours pour toutes les voitures
    lap_counters = [LapCounter(game_map.checkpoints) for _ in range(len(cars))]
    
    checkpoint_claimed = [False] * len(game_map.checkpoints)

    previous_positions = [car.position.copy() for car in cars]

    running = True
    max_time = 2000  # Temps maximum avant la fin de la génération
    current_time = 0

    while running and len(cars) > 0 and current_time < max_time:
        pygame.display.flip()
        # Dessine l'environnement
        game_map.draw(screen)

        # Calcul du delta temps réel en utilisant l'horloge
        dt = clock.tick(60) / 1000  # Delta temps en secondes (temps réel)

        # Limite le delta temps pour éviter des sauts trop grands (utile quand les FPS chutent)
        dt = min(dt, 1 / 30)  # Limite dt à un maximum de 1/30 de seconde
        current_time += 1  # Incrémente le temps

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    raycast_visible = not raycast_visible  # Affiche ou masque les rayons

        for i in range(len(cars)):
            car = cars[i]

            if not car.active:
                continue  # Ignore les voitures inactives

            # Mise à jour de la voiture
            distances, endpoints = raycast.cast_rays(car.position, car.angle, game_map.road_surface)

            car.draw(screen)

            if raycast_visible:
                raycast.draw_rays(screen, car.position, endpoints)

            # Normalise les distances pour le réseau neuronal
            inputs = [distance / 200 for distance in distances]  # Supposons une distance maximale de 200 pixels
            inputs.append(car.speed / CAR_MAX_SPEED)  # Normalise la vitesse
            inputs.append(car.angle / 360)  # Normalise l'angle

            # Donne les entrées au réseau
            output = nets[i].activate(inputs)

            # Contrôle par le réseau neuronal :
            # output[0] = accélérer ou décélérer
            # output[1] = tourner à gauche ou à droite

            # Logique d'accélération/décélération
            if output[0] > 0.5:
                car.speed += CAR_ACCELERATION * dt  # Accélère la voiture
            elif output[0] <= 0.5:
                car.speed -= CAR_ACCELERATION * dt  # Décélère la voiture
                car.speed = max(car.speed, CAR_MIN_SPEED)

            # Logique de rotation
            if output[1] > 0.5 and abs(car.speed) > 0:
                car.angle -= CAR_TURN_SPEED * dt  # Tourne à droite
            elif output[1] <= 0.5 and abs(car.speed) > 0:
                car.angle += CAR_TURN_SPEED * dt  # Tourne à gauche

            car.update(dt)  # Mise à jour de la voiture

            # Vérifie le passage des checkpoints
            previous_laps = lap_counters[i].laps_completed
            previous_checkpoints = lap_counters[i].current_checkpoint

            

            lap_counters[i].check_checkpoint(previous_positions[i], car.position)
            previous_positions[i] = car.position.copy()

            # Récompense pour passer un checkpoint
            if lap_counters[i].current_checkpoint > previous_checkpoints:
                cp = previous_checkpoints  # numéro du checkpoint atteint

                # Récompense normale
                ge[i].fitness += 100

                # Bonus si c’est la première voiture à passer ce checkpoint
                if not checkpoint_claimed[cp]:
                    ge[i].fitness += 200      # BONUS pour le premier
                    checkpoint_claimed[cp] = True

            # Récompense pour terminer un tour
            if lap_counters[i].laps_completed > previous_laps:
                ge[i].fitness += 10000  # Très grande récompense pour un tour complété

            # Décroissance de la fitness : petite pénalité pour encourager un mouvement rapide
            ge[i].fitness -= 0.001  # Petite décroissance au fil du temps

            # Récompense pour le mouvement : si la voiture avance, récompense basée sur la distance parcourue
            distance_traveled = previous_positions[i].distance_to(car.position)
            ge[i].fitness += distance_traveled * 1  # Récompense pour avancer
            
            ge[i].fitness -= 1  # Petite pénalité pour rester bloqué
            
            if(cars[i].speed<80):
                ge[i].fitness -= 3
            
            # Vérifie la collision
            if car.check_collision(game_map):
                ge[i].fitness -= 4000  # Pénalise la collision
                car.active = False  # Marque la voiture comme inactive

        # Arrête si toutes les voitures sont bloquées et ne progressent pas
        if all(not car.active or (abs(car.speed) <= 1 and ge[i].fitness < 0.1) for i, car in enumerate(cars)):
            break

# Point d'entrée du script
if __name__ == "__main__":
    # Chemin vers le fichier de configuration NEAT
    config_path = "config-feedforward.txt"

    # Vérifie si un fichier de checkpoint doit être chargé
    checkpoint_path = "checkpoint/neat-checkpoint-836"  # Définit le chemin du fichier de checkpoint à charger
    if len(sys.argv) > 1:
        checkpoint_path = sys.argv[1]


    run_neat(config_path, checkpoint_path)
