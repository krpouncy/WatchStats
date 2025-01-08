from models import PredictorInterface

class UserPredictor(PredictorInterface):
    def get_stats_and_details(self, filename):
        """
        Abstract method to get the stats and game details from the given filename.
        :param filename: The name of the file to get the stats and game details from.
        :return: A tuple containing the stats and game details.
        """
        return None

    def predict_probability(self, stats, game_details):
        """
        Abstract method to predict the probability of winning based on the given stats and game details.
        :param stats: A list of leaderboard stats relevant for win predictions.
        :param game_details: A tuple containing game_details.
        :return: The probability of winning the game.
        """
        return 0.5