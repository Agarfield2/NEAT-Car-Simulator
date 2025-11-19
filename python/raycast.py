import pygame
import math

class Raycast:
    def __init__(self, angles):
        """
        Initialise l'objet Raycast avec une liste d'angles.

        Paramètres :
            angles : list
                Liste des angles en degrés pour les rayons.
        """
        self.angles = angles  # Liste des angles en degrés

    def cast_rays(self, car_position, car_angle, map_surface):
        """
        Lance des rayons à partir de la position de la voiture pour détecter les obstacles.

        Paramètres :
            car_position : tuple (float, float)
                La position actuelle de la voiture (x, y).
            car_angle : float
                L'angle actuel de la voiture en degrés.
            map_surface : pygame.Surface
                La surface de la carte sur laquelle les rayons sont projetés.

        Retourne :
            tuple : (list, list)
                distances : Liste des distances pour chaque rayon.
                end_points : Liste des points d'extrémité pour chaque rayon.
        """
        distances = []
        end_points = []
        for angle in self.angles:
            # Calcule l'angle total en ajoutant l'angle du rayon à l'angle de la voiture
            total_angle = car_angle + angle
            rad_angle = math.radians(total_angle)  # Convertit l'angle en radians

            # Point de départ du rayon
            x0, y0 = car_position

            # Vecteur de direction
            dx = -math.sin(rad_angle)
            dy = -math.cos(rad_angle)

            distance = 0
            max_distance = 200  # Distance maximale pour vérifier les obstacles
            step = 1  # Taille de l'étape en pixels

            # Parcours le rayon jusqu'à la distance maximale
            while distance < max_distance:
                x = x0 + dx * distance
                y = y0 + dy * distance

                # Vérifie si le rayon sort des limites de la carte
                if x < 0 or x >= map_surface.get_width() or y < 0 or y >= map_surface.get_height():
                    break

                # Obtient la couleur du pixel à la position actuelle
                color = map_surface.get_at((int(x), int(y)))

                # Suppose que l'herbe est verte (0, 200, 0), arrête si le rayon touche l'herbe
                if color == (0, 200, 0, 255):  # Inclut le canal alpha
                    break

                distance += step

            # Ajoute la distance trouvée et le point d'extrémité du rayon
            distances.append(distance)
            end_point = (x0 + dx * distance, y0 + dy * distance)
            end_points.append(end_point)

        return distances, end_points

    def draw_rays(self, screen, car_position, end_points):
        """
        Dessine les rayons sur l'écran à partir de la position de la voiture jusqu'aux points d'extrémité.

        Paramètres :
            screen : pygame.Surface
                L'écran sur lequel les rayons doivent être dessinés.
            car_position : tuple (float, float)
                La position actuelle de la voiture (x, y).
            end_points : list
                Liste des points d'extrémité pour chaque rayon.
        """
        for end_point in end_points:
            # Dessine une ligne entre la position de la voiture et le point d'extrémité du rayon
            pygame.draw.line(screen, (24, 196, 201), car_position, end_point, 1)