# app/core/predictor_interface.py
from abc import ABC, abstractmethod

class PredictorInterface(ABC):
    @abstractmethod
    def get_stats_and_details(self, filename):
        """
        Abstract method to get the stats and game details from the given filename.
        :param filename: The name of the file to get the stats and game details from.
        :return: A tuple containing the stats and game details.
        """
        pass

    @abstractmethod
    def predict_probability(self, stats, game_details):
        """
        Abstract method to predict the probability of winning based on the given stats and game details.
        :param stats: A list of leaderboard stats relevant for win predictions.
        :param game_details: A tuple containing game_details.
        :return: The probability of winning the game.
        """
        pass

class EventsHandlerInterface(ABC):
    @abstractmethod
    def handle_event(self, socket_object, event_name, payload=None):
        """
        Abstract method to handle the given event with the given payload.
        """

        # established events: game_details, game_outcome_set, page_load

        # EXAMPLE:
        # if event_name == "game_details":
        #     # calculate the team_status and update the player status
        #     stats, game_details, win_probability = payload
        #     time, team_composition = game_details
        #
        #     # Use the socket object to emit information to the web server
        #     socket_object.emit('game_details', payload)
        pass
