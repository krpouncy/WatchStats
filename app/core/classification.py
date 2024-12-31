# app/core/classification.py
import re

import cv2
import numpy as np
import pytesseract

from app import socketio
from app.core.game_manager import game_manager
from app.core.image_parser import ImageParser
from app.core.image_utils import generate_sub_images
from app.core.state import app_state


# create a classifier object to compute logistic regression
class LogisticRegression:
    def __init__(self):
        # initialize the coefficients for the model as None
        self.threshold = None
        self.sensitivity = None
        self.specificity = None
        self.intercept = None
        self.time_coeff = None
        self.player_coefficients = None
        self.support_status_coef = None
        self.tank_status_coef = None
        self.dps_status_coef = None

        # initialize the model with chosen coefficients
        self.init_version_1()

    def init_version_1(self):
        # initialize the coefficients for the model
        self.threshold = 0.5187982
        self.sensitivity = 0.6979
        self.specificity = 0.6460
        self.intercept = -0.2182999
        self.time_coeff = 0.03752734

        self.player_coefficients = np.array([
            # Player 0
            [-0.06960857, 0.08510925, 0.9270883, -0.0002490955, 0.0001611925, -0.0001437304],

            # Player 1
            [-0.1892463, 0.1117381, 0.3582217, -0.000007660653, 0.001749342, 0.001472445],

            # Player 2
            [-0.1502424, 0.1142032, 0.2539363, -0.0001045803, 0.0004350601, 0.001241053],

            # Player 3
            [0.01487998, -0.2174127, 0.4152493, -0.0004105658, 0.0002817601, 0.0006214099],

            # Player 4
            [-0.04825786, -0.1690310, 0.6637459, -0.0003865351, 0.00001735066, -0.0009142630]
        ])

        self.support_status_coef = {
            'poor': -0.7340903,
            'average': 0.0,
            'good': -0.1827037
        }
        self.tank_status_coef = {
            'poor': -0.4417093,
            'average': 0.0,
            'good': -0.7142583
        }
        self.dps_status_coef = {
            'poor': 0,
            'average': 0,
            'good': 0
        }

    def predict_probability(self, stats, game_details):
        """Predicts the probability of winning a game based on the given stats and game details."""

        time_in_minutes, team_composition, team_status = game_details

        # return nothing if the there are 5 or more players missing
        if not stats or len(stats) < 5 or time_in_minutes is None:
            print(len(stats), stats)
            return None

        if time_in_minutes < 1.0:
            time_in_minutes = 1

        # ensure that team_status is at least average
        team_status = ["average" if x == "not enough data" else x for x in team_status]

        feature_vector = [self.intercept,
                          time_in_minutes * self.time_coeff,
                          self.tank_status_coef[team_status[0]],
                          self.support_status_coef[team_status[2]]] # TODO assumes that dps isn't used for prediction

        # print the stats
        print("Stats:", stats)

        for i, player_stats in enumerate(stats[:5]):
            player_row = [val / time_in_minutes for val in player_stats]

            player_row[0] = min(player_row[0], 5)  # cap kills
            player_row[1] = min(player_row[1], 4)  # cap assists
            player_row[2] = min(player_row[2], 3)  # cap deaths
            player_row[3] = min(player_row[3], 2500)  # cap damage

            if i == 0:
                player_row[4] = min(player_row[4], 600)  # cap tank heals
            elif i in [1, 2]:
                player_row[4] = min(player_row[4], 400)  # cap damage heals
            else:
                player_row[4] = min(player_row[4], 2500)  # cap support heals

            player_row[5] = min(player_row[5], 2500)  # cap tank MIT

            contrib = np.dot(self.player_coefficients[i], player_row)
            feature_vector.append(contrib)

        winning_chances = 1 / (1 + np.exp(sum(feature_vector)))
        print(f"Computed Winning Probability: {winning_chances:.2f}")

        lr_positive = self.sensitivity / (1 - self.specificity)
        lr_negative = (1 - self.sensitivity) / self.specificity

        odds_prior = winning_chances / (1 - min(winning_chances, 0.9999))
        if winning_chances > self.threshold:
            odds_posterior = odds_prior * lr_positive
        else:
            odds_posterior = odds_prior * lr_negative

        posterior_prob = odds_posterior / (1 + odds_posterior)
        return posterior_prob

def convert_stats_to_int(stats):
    for i in range(len(stats)):
        for j in range(len(stats[i])):
            if stats[i][j] == '':
                stats[i][j] = 0
            else:
                stats[i][j] = int(stats[i][j])

    return stats

def calculate_team_statuses(stats):
    """Calculate the status of the tank, dps, and support roles based on the given stats.

    :param stats: A list of 5 lists (representing players on Team) with each containing 6 numeric values for K, A, D, Dmg, H, and MIT.
    :return: A tuple of strings representing the status of the tank, dps, and support roles.
    """

    # initialize the status of each role
    tank_status, dps_status, support_status = 'not enough data', 'not enough data', 'not enough data'

    # calculate the tank, dps, and support status
    tank_k, tank_mit = stats[0][0], stats[0][5]
    if tank_k != 0 and tank_mit != 0:
        tank_ratio = tank_k / (tank_k + tank_mit**0.5)
        if tank_ratio <= 0.05:
            tank_status = 'poor'
        elif 0.04 < tank_ratio < 0.08:
            tank_status = 'average'
        else:
            tank_status = 'good'

    dps_damage = stats[1][3] + stats[2][3]
    enemy_dps_damage = stats[6][3] + stats[7][3]
    if dps_damage != 0 and enemy_dps_damage != 0:
        if abs(dps_damage - enemy_dps_damage) < 274:
            dps_status = 'average'
        elif dps_damage - enemy_dps_damage >= 274:
            dps_status = 'good'
        else:
            dps_status = 'poor'

    damage = stats[3][3] + stats[4][3]
    healing = stats[3][4] + stats[4][4]
    if damage != 0 and healing != 0:
        if damage + healing > 0:
            damage_ratio = damage / (damage + healing)
        else:
            damage_ratio = 0.0

        print(f"Damage Ratio: {damage_ratio:.2f}. Feedback: ", end="")

        if damage_ratio < 0.14:
            print("SHOOT!")
            support_status = 'poor'
        elif 0.185 <= damage_ratio <= 0.32:
            print("You're doing good.")
            support_status = 'average'
        else:
            support_status = 'good'

    return tank_status, dps_status, support_status

def get_stats_and_details(filename):
    """
    Extract the stats and details from the given image.
    :param filename: The filename of the image.
    :return: A tuple of stats and game details. None if the image could not be read or the dimensions are too small.
    """
    image = cv2.imread(filename)
    if image is None:
        print(f"Error reading image: {filename}")
        return None

    if image.shape[0] < 100 or image.shape[1] < 750:
        print(f"Image dimensions are too small: {image.shape}")
        return None

    header_image = image[:100, 120:750]
    custom_config = r'--oem 3 --psm 6'
    header_text = pytesseract.image_to_string(header_image, config=custom_config)
    details = [line.strip() for line in header_text.split('\n') if line.strip()]

    time_in_minutes = None
    for detail in details:
        if 'TIME:' in detail:
            time_str = detail.split('TIME:')[-1].strip()
            match = re.match(r"(?:(\d+):)?(\d+)(?:\.(\d+))?", time_str)
            if match:
                minutes = int(match.group(1)) if match.group(1) else 0
                seconds = int(match.group(2))
                time_in_minutes = minutes + seconds / 60.0
            else:
                try:
                    time_in_minutes = float(time_str)
                except ValueError:
                    print(f"Could not parse time: {time_str}")
                    time_in_minutes = None
            break

    sub_images = generate_sub_images(filename)

    # crop and parse character images
    character_images = [si[:, :91] for si in sub_images]
    team_composition, _ = classifier.classify_images(character_images, skip_enemy=True) # TODO process images in batch

    # crop and parse stat images
    stat_images = [si[:, 91:] for si in sub_images]
    stats = classifier.extract_text_from_stats(stat_images)
    stats = convert_stats_to_int(stats) # convert stats to integers
    team_status = calculate_team_statuses(stats)

    return stats, (time_in_minutes, team_composition, team_status)

def process_screenshot():
    """Process the current screenshot and update the win probability."""
    filename = game_manager.take_screenshot()

    socketio.emit('screenshot_taken', {'filename': filename})
    socketio.emit('show_loading_overlay')
    details = get_stats_and_details(filename)
    socketio.emit('hide_loading_overlay')

    if details is not None:
        stats, game_details = details
        prob = prediction_model.predict_probability(stats, game_details)

        if prob is not None:
            app_state.game_progress.append(prob)
            socketio.emit('update_chart', {'win_probability': prob})
            print(f"Updated Win Probability: {prob}")

            _, team_composition, team_status = game_details
            update_player_status(team_status, team_composition)
        else:
            game_manager.current_screenshots.pop()
    else:
        game_manager.current_screenshots.pop()

def update_player_status(team_status, team_composition):
    """Update the player status based on the given team status and composition."""
    # remove the label_ prefix from each person in the team
    team_players = ['_'.join(player.split('_')[1:]) for player in team_composition]
    print(team_players)

    tank_status, dps_status, support_status = team_status

    socketio.emit('performance_update', {
        'tank': {'status': tank_status, 'text': 'Tank: ' + tank_status},
        'damage': {'status': dps_status, 'text': 'Damage: ' + dps_status},
        'support': {'status': support_status, 'text': 'Support: ' + support_status},
        'team_composition': team_players
    })

# initialize the classifier and prediction model
prediction_model = LogisticRegression()

if app_state.model_path is None:
    print("Model path not set.")
else:
    print(f"Model path: {app_state.model_path}")
    classifier = ImageParser(model_path=app_state.model_path)