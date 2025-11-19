# NEAT Car Project - AI Club

## Description

This project simulates the behavior of an autonomous car using the NEAT algorithm (NeuroEvolution of Augmenting Topologies).
The initial code skeleton was provided by the AI Club, and I contributed the following parts:

* Model training
* Data preprocessing
* Performance visualization
* Model parameter optimization

## Technologies and Libraries Used

* Python 3.x
* [NEAT-Python](https://neat-python.readthedocs.io/)
* [Pygame](https://www.pygame.org/) for visual simulation
* Matplotlib, NumPy, Pandas for data processing and visualization
* Pickle for saving/loading trained models

## Features

* Simulates an autonomous car in a 2D environment with Pygame
* Evolves a neural network using NEAT
* Visualizes car trajectories and performance metrics
* Hyperparameter tuning to improve performance
* Save and load the best trained model with Pickle
* Manual driving using the keyboard

## Main Scripts

| Script                      | Description                                                    |
| --------------------------- | -------------------------------------------------------------- |
| `main_neat.py`              | Trains the NEAT model on the track and saves the best network. |
| `FINAL_CAR_RACE.py`         | Loads the best model and runs the car automatically.           |
| `main_drive_it_yourself.py` | Allows manual control of the car via keyboard.                 |

## Installation and Environment

### Create a virtual environment

```bash
python3 -m venv env
```

### Activate the environment

* On Windows:

```bash
.\env\Scripts\activate
```

* On Linux/macOS:

```bash
source ./env/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

* **Train the model**:

```bash
python main_neat.py
```

* **Automatic race with the best model**:

```bash
python FINAL_CAR_RACE.py
```

* **Manual driving**:

```bash
python main_drive_it_yourself.py
```

## Results

* Performance graphs and car trajectories are saved in the `results/` folder.
* Optimized parameters and training logs are saved for analysis.

## Contribution

* Project completed as part of the **AI Club**.
* Personal contributions: training, preprocessing, visualization, and hyperparameter tuning.
* The original code skeleton was provided by the club.

## License

* For educational and portfolio use only.
