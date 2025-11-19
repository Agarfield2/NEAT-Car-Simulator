import math
import pygame

class Car:
    def __init__(self, x, y, image_path= "Car_red_Frong.png", width=20, height=40, max_speed=200, acceleration=200, turn_speed=180, min_speed=0):
        """
        Initialise une voiture avec sa position, ses caractéristiques de mouvement et son image.
        :param x: Position initiale en x.
        :param y: Position initiale en y.
        :param image_path: Chemin de l'image de la voiture.
        :param width: Largeur de l'image de la voiture.
        :param height: Hauteur de l'image de la voiture.
        :param max_speed: Vitesse maximale de la voiture.
        :param acceleration: Accélération de la voiture.
        :param turn_speed: Vitesse de rotation de la voiture.
        """
        self.width = width  # Largeur de la voiture
        self.height = height  # Hauteur de la voiture
        self.position = pygame.Vector2(x, y)  # Position de la voiture (vecteur 2D)
        self.velocity = pygame.Vector2(0, 0)  # Vitesse actuelle (vecteur 2D)
        self.lateral_velocity = 0  # Vitesse latérale pour simuler les dérapages
        self.angle = -90  # Angle initial de la voiture en degrés
        self.speed = 0  # Vitesse initiale
        self.max_speed = max_speed  # Vitesse maximale réglable
        self.min_speed = min_speed # Vitesse minimal réglable
        self.acceleration = acceleration  # Accélération réglable
        self.deceleration = acceleration  # Utilisation de la même valeur pour la décélération
        self.turn_speed = turn_speed  # Vitesse de rotation réglable
        self.drift_factor = 0.8  # Facteur de dérapage (contrôle l'intensité du dérapage)

        # Chargement et préparation de l'image de la voiture
        self.surface = pygame.image.load(image_path).convert_alpha()  # Chargement de l'image avec transparence
        self.surface = pygame.transform.scale(self.surface, (self.width, self.height))  # Mise à l'échelle de l'image
        self.surface = pygame.transform.rotate(self.surface, 180)  # Rotation initiale de l'image

        self.active = True  # Indique si la voiture est toujours en course (active)

    def update(self, dt):
        """
        Met à jour la position et la vitesse de la voiture en fonction de la vitesse actuelle, de l'angle, et du dérapage.
        :param dt: Temps écoulé depuis la dernière mise à jour (delta time).
        """
        # Limiter la vitesse
        self.speed = max(min(self.speed, self.max_speed), -self.max_speed / 2)

        # Effet de dérapage : la vitesse latérale est influencée par la vitesse et l'angle de rotation
        if abs(self.speed) > self.max_speed * 0.5 and abs(self.lateral_velocity) < 20:  # Seuil pour activer le dérapage
            self.lateral_velocity += (self.turn_speed * dt) * self.drift_factor

        # Réduction progressive de la vitesse latérale (friction)
        self.lateral_velocity *= 0.95

        # Mise à jour de la position
        rad_angle = math.radians(self.angle)  # Conversion de l'angle en radians

        # Mouvement vers l'avant
        self.velocity.x = -self.speed * math.sin(rad_angle)  # Calcul de la composante x de la vitesse
        self.velocity.y = -self.speed * math.cos(rad_angle)  # Calcul de la composante y de la vitesse

        # Mouvement latéral (pendant le dérapage)
        drift_vector = pygame.Vector2(self.lateral_velocity * math.cos(rad_angle),
                                      self.lateral_velocity * math.sin(rad_angle))

        # Mise à jour de la position avec les mouvements vers l'avant et latéral (dérapage)
        self.position += (self.velocity + drift_vector) * dt

    def draw(self, screen):
        """
        Dessine la voiture sur l'écran.
        :param screen: Surface de l'écran sur laquelle la voiture sera dessinée.
        """
        # Rotation de l'image de la voiture
        rotated_surface = pygame.transform.rotate(self.surface, self.angle)
        rect = rotated_surface.get_rect(center=self.position)  # Création d'un rectangle centré sur la position actuelle
        screen.blit(rotated_surface, rect)  # Dessiner l'image de la voiture sur l'écran

    def check_collision(self, map_instance):
        """
        Vérifie les collisions pixel par pixel avec les zones d'herbe sur la carte à l'aide de masques.
        :param map_instance: Instance de la carte avec laquelle la voiture peut entrer en collision.
        :return: True si une collision est détectée, sinon False.
        """
        # Rotation de l'image de la voiture et création d'un masque
        rotated_surface = pygame.transform.rotate(self.surface, self.angle)
        rotated_mask = pygame.mask.from_surface(rotated_surface)  # Création d'un masque à partir de l'image
        rect = rotated_surface.get_rect(center=self.position)

        # Décalage pour la vérification de chevauchement des masques
        offset = (int(rect.left), int(rect.top))

        # Vérifier le chevauchement entre le masque de la voiture et le masque de l'herbe de la carte
        if map_instance.grass_mask.overlap(rotated_mask, offset):
            return True  # Collision détectée

        return False

    def reset(self, start_position):
        """
        Réinitialise la voiture à la position de départ et remet à zéro la vitesse, l'angle, et la vitesse latérale.
        :param start_position: Position de départ (vecteur 2D).
        """
        self.position = pygame.Vector2(start_position)  # Réinitialiser la position
        self.velocity = pygame.Vector2(0, 0)  # Réinitialiser la vitesse
        self.lateral_velocity = 0  # Réinitialiser la vitesse latérale
        self.speed = 0  # Réinitialiser la vitesse
        self.angle = -90  # Réinitialiser l'angle de la voiture