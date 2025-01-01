# app/core/game_manager.py

import datetime
import os
import shutil

import eventlet
from PIL import ImageGrab

from .state import app_state


class GameManager:
    def __init__(self, screenshot_folder='screenshots'):
        self.earliest_timestamp = None
        self.current_screenshots = []
        self.screenshot_folder = screenshot_folder

        #print current working directory
        print("Current working directory: ", os.getcwd())

    def create_game_folder(self, game_result):
        """Create a folder for the current game."""
        if self.earliest_timestamp is None:
            self.earliest_timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        folder_name = os.path.join(self.screenshot_folder, f"game_{game_result}_{self.earliest_timestamp}")
        os.makedirs(folder_name, exist_ok=True)
        return folder_name

    def take_screenshot(self):
        """Take a screenshot and save it to the screenshot folder."""
        eventlet.sleep(0.25)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        if self.earliest_timestamp is None:
            self.earliest_timestamp = timestamp
        filename = os.path.join(self.screenshot_folder, f"screenshot_{timestamp}.png")
        screenshot = ImageGrab.grab()
        screenshot.save(filename, 'JPEG', quality=85)
        print(f"Screenshot saved as {filename}")
        self.current_screenshots.append(filename)
        return filename

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

game_manager = GameManager()
if app_state.screenshot_folder:
    game_manager.screenshot_folder = app_state.screenshot_folder

