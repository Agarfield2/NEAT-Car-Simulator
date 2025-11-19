# Projet Voiture NEAT - Club IA

## Description

Ce projet simule le comportement d’une voiture autonome à l’aide de l’algorithme NEAT (NeuroEvolution of Augmenting Topologies).
Le squelette du code a été fourni par le club IA, et j’ai développé les parties suivantes :

* Entraînement du modèle
* Préprocessing des données
* Visualisation des performances
* Optimisation des paramètres du modèle

## Technologies et librairies utilisées

* Python 3.x
* [NEAT-Python](https://neat-python.readthedocs.io/)
* [Pygame](https://www.pygame.org/) pour la simulation visuelle
* Matplotlib, NumPy, Pandas pour visualisations et traitement
* Pickle pour sauvegarder/recharger les modèles

## Fonctionnalités

* Simulation d’une voiture autonome sur un environnement 2D avec Pygame
* Évolution d’un réseau neuronal grâce à NEAT
* Visualisation des trajectoires et performances
* Ajustement des hyperparamètres pour améliorer la performance
* Sauvegarde et chargement du meilleur modèle via Pickle
* Conduite manuelle de la voiture avec le clavier

## Scripts principaux

| Script                      | Description                                                            |
| --------------------------- | ---------------------------------------------------------------------- |
| `main_neat.py`              | Entraîne le modèle NEAT sur la piste et sauvegarde le meilleur réseau. |
| `FINAL_CAR_RACE.py`         | Charge le meilleur modèle et fait courir la voiture automatiquement.   |
| `main_drive_it_yourself.py` | Permet de contrôler la voiture manuellement avec le clavier.           |

## Installation et environnement

### Créer un environnement virtuel

```bash
python3 -m venv env
```

### Activer l’environnement

* Sous Windows :

```bash
.\env\Scripts\activate
```

* Sous Linux / macOS :

```bash
source ./env/bin/activate
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

## Exécution du projet

* **Entraînement du modèle** :

```bash
python main_neat.py
```

* **Course automatique avec le meilleur modèle** :

```bash
python FINAL_CAR_RACE.py
```

* **Conduite manuelle** :

```bash
python main_drive_it_yourself.py
```

## Résultats

* Graphiques des performances et trajectoires des voitures générés dans le dossier `results/`.
* Les paramètres optimisés et logs d’entraînement sont sauvegardés pour analyse.

## Contribution

* Projet réalisé dans le cadre du **club IA**.
* Contribution personnelle : entraînement, préprocessing, visualisation et ajustement des paramètres.
* Le code original du squelette a été fourni par le club.

## Licence

* À utiliser à des fins éducatives / portfolio uniquement.
