import pygame

def line_intersect(a1, a2, b1, b2):
    """
    Détermine si les segments de droite a1a2 et b1b2 se croisent.

    Paramètres :
        a1, a2 : tuples ou listes (float, float)
            Les points définissant le premier segment de droite.
        b1, b2 : tuples ou listes (float, float)
            Les points définissant le deuxième segment de droite.

    Retourne :
        bool : True si les segments se croisent, sinon False.
    """
    # Définition d'une fonction interne pour vérifier l'orientation des points
    def ccw(A, B, C):
        # Retourne True si les points A, B, C sont dans le sens anti-horaire
        return (C.y - A.y) * (B.x - A.x) > (B.y - A.y) * (C.x - A.x)

    # Conversion des points en vecteurs Pygame
    A = pygame.Vector2(a1)
    B = pygame.Vector2(a2)
    C = pygame.Vector2(b1)
    D = pygame.Vector2(b2)

    # Vérifie si les segments se croisent en utilisant les orientations
    return (ccw(A, C, D) != ccw(B, C, D)) and (ccw(A, B, C) != ccw(A, B, D))

class LapCounter:
    def __init__(self, checkpoints):
        """
        Initialise le compteur de tours avec une liste de checkpoints.

        Paramètres :
            checkpoints : list
                Liste de dictionnaires contenant les checkpoints avec des clés 'start', 'end', et 'order'.
        """
        # Trie les checkpoints en fonction de leur ordre
        self.checkpoints = sorted(checkpoints, key=lambda x: x['order'])
        # Initialise l'indice du checkpoint actuel
        self.current_checkpoint = 0
        # Initialise le nombre de tours complétés
        self.laps_completed = 0

    def check_checkpoint(self, old_pos, new_pos):
        """
        Vérifie si le joueur a passé un checkpoint en se déplaçant de l'ancienne position à la nouvelle position.

        Paramètres :
            old_pos : tuple ou liste (float, float)
                Position précédente du joueur.
            new_pos : tuple ou liste (float, float)
                Nouvelle position du joueur.
        """
        # Vérifie si tous les checkpoints ont été franchis
        if self.current_checkpoint >= len(self.checkpoints):
            # Tous les checkpoints ont été franchis, commence un nouveau tour
            self.current_checkpoint = 0
            self.laps_completed += 1
            #print(f"Tour complété ! Total des tours : {self.laps_completed}")

        # Récupère le checkpoint actuel
        checkpoint = self.checkpoints[self.current_checkpoint]
        start = checkpoint['start']
        end = checkpoint['end']

        # Vérifie si la trajectoire entre l'ancienne et la nouvelle position croise le checkpoint
        if line_intersect(old_pos, new_pos, start, end):
            # Incrémente l'indice du checkpoint actuel
            self.current_checkpoint += 1
            #print(f"Checkpoint {checkpoint['order']} franchi !")