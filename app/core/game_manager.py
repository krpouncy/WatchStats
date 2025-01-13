# app/core/game_manager.py

import datetime
import importlib
import os
import shutil

import eventlet
from PIL import ImageGrab

from app import socketio
from models import PredictorInterface, EventsHandlerInterface, HandlerEvent
from .state import app_state

# Create empty classes for testing purposes
class DummyPredictorInterface(PredictorInterface):
    def predict_probability(self, stats, game_details):
        return 0.5

    def get_stats_and_details(self, filename):
        return None

class DummyEventsHandlerInterface(EventsHandlerInterface):
    def handle_event(self, socket_object, event_name, payload=None):
        pass

class GameManager:
    def __init__(self, screenshot_folder='screenshots'):
        self.earliest_timestamp = None
        self.current_screenshots = []
        self.screenshot_folder = screenshot_folder

        # initialize the predictor and events handler
        self.predictor = DummyPredictorInterface()
        self.events_handler = DummyEventsHandlerInterface()

        # print current working directory
        print("Current working directory: ", os.getcwd())

    def create_game_folder(self, game_result):
        """Create a folder for the current game."""
        if self.earliest_timestamp is None:
            self.earliest_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = os.path.join(self.screenshot_folder, f"game_{game_result}_{self.earliest_timestamp}")
        os.makedirs(folder_name, exist_ok=True)
        return folder_name

    def take_screenshot(self, delay=0.25, image_format='JPEG', quality=85):
        """
        Take a screenshot and save it to the screenshot folder.

        :param delay: Delay in seconds before taking the screenshot. (default: 0.25)
        :param image_format: Image format to save the screenshot. (default: 'JPEG') Options: BMP, JPEG, TIFF, PNG.
        :param quality: Image quality (0-100) for the saved screenshot. (default: 85)
        """
        eventlet.sleep(delay)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if self.earliest_timestamp is None:
            self.earliest_timestamp = timestamp
        filename = os.path.join(self.screenshot_folder, f"screenshot_{timestamp}.png")
        screenshot = ImageGrab.grab()
        screenshot.save(filename, image_format, quality=quality)
        print(f"Screenshot saved as {filename}")
        self.current_screenshots.append(filename)
        return filename

    def process_screenshot(self):
        """Process the current screenshot and update the win probability."""
        socketio.emit('show_loading_overlay')
        socketio.sleep(0.25)  # this is necessary and allows the loading overlay to be displayed
        filename = self.take_screenshot()

        socketio.emit('screenshot_taken', {'filename': filename})
        details = self.get_stats_and_details(filename)
        socketio.emit('hide_loading_overlay')

        if details is not None:
            stats, game_details = details
            prob = self.predict_probability(stats, game_details)

            # add win probability to the game details to the tuple
            game_details = (game_details[0], game_details[1], prob)  # TODO make this more flexible REMOVE

            # call the custom event handler to process the game details
            self.events_handler.handle_event(socketio, HandlerEvent.GAME_DETAILS, (stats, game_details))
        else:
            self.current_screenshots.pop()  # TODO make this more flexible by making optional to remove if no details

    def move_screenshots_to_folder(self, game_result):
        """Move the current screenshots to a folder for the current game."""
        folder = self.create_game_folder(game_result)
        if not self.current_screenshots:
            print("No screenshots to move.")
            return folder

        print(f"Moving {len(self.current_screenshots)} screenshots to {folder}")
        for shot in self.current_screenshots:
            if os.path.exists(shot):
                new_path = os.path.join(folder, os.path.basename(shot))
                shutil.move(shot, new_path)
                print(f"Moved {shot} -> {new_path}")
            else:
                print(f"Warning: Screenshot not found: {shot}")

        self.current_screenshots.clear()
        self.earliest_timestamp = None
        return folder

    def load_model(self, model_name):
        """Load the user models and event handlers."""
        print(f"Attempting to load model: {model_name}")
        if model_name:
            try:
                self.predictor = self.load_user_predictor(model_name)
                self.events_handler = self.load_user_events_handler(model_name)
                print(f"Successfully loaded model: {model_name}")
            except Exception as e:
                print(f"Error loading {model_name} predictor: {e}")
                # print traceback
                import traceback
                traceback.print_exc()
        else:
            print("No model name provided. Predictor set to None.")
            self.predictor = None

    def load_user_predictor(self, model_name):
        """Load the user predictor class from the model directory."""
        model_path = os.path.join(app_state.model_directory, model_name, 'predictor.py')
        print(f"Loading user predictor from path: {model_path}")

        if not os.path.exists(model_path):
            print(f"Model script not found at {model_path}")
            raise ImportError(f"Model script not found at {model_path}")

        spec = importlib.util.spec_from_file_location("user_predictor", model_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("Module successfully loaded.")

        predictor_class = getattr(module, 'UserPredictor', None)
        if not predictor_class:
            print("User predictor class 'UserPredictor' not found in the script.")
            raise ImportError("User predictor class 'UserPredictor' not found in the script.")

        if not issubclass(predictor_class, PredictorInterface):
            print("User predictor does not implement PredictorInterface.")
            raise TypeError("User predictor must implement PredictorInterface.")

        print("User predictor class successfully validated.")
        return predictor_class()

    def load_user_events_handler(self, model_name):
        """Load the user events handler class from the model directory."""
        model_path = os.path.join(app_state.model_directory, model_name, 'events_handler.py')
        print(f"Loading user events handler from path: {model_path}")

        if not os.path.exists(model_path):
            print(f"Model script not found at {model_path}")
            raise ImportError(f"Model script not found at {model_path}")

        spec = importlib.util.spec_from_file_location("user_events_handler", model_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("Module successfully loaded.")

        events_handler_class = getattr(module, 'UserEventsHandler', None)
        if not events_handler_class:
            print("User events handler class 'UserEventsHandler' not found in the script.")
            raise ImportError("User events handler class 'UserEventsHandler' not found in the script.")

        if not issubclass(events_handler_class, EventsHandlerInterface):
            print("User events handler does not implement EventsInterface.")
            raise TypeError("User events handler must implement EventsInterface.")

        print("User events handler class successfully validated.")
        return events_handler_class()

    def predict_probability(self, stats, game_details):
        """Predict the win probability for the current game."""
        # print(f"Predicting probability with stats: {stats} and game details: {game_details}")
        if self.predictor:
            try:
                result = self.predictor.predict_probability(stats, game_details)
                print(f"Prediction result: {result}")

                # send the output to the event handler
                self.events_handler.handle_event(socketio, HandlerEvent.GAME_PREDICTION, result)

                return result
            except Exception as e:
                print(f"Error predicting probability: {e}")
                return None
        else:
            print("No model loaded. Cannot predict probability.")
            return None

    def get_stats_and_details(self, filename):
        """Get the stats and details for the current game."""
        print(f"Getting stats and details from filename: {filename}")
        if self.predictor:
            try:
                return self.predictor.get_stats_and_details(filename)
            except Exception as e:
                print(f"Error getting stats and details: {e}")
                return None
        else:
            print("No model loaded. Cannot get stats and details.")
            return None


game_manager = GameManager()
