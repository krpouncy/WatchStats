import os
import sys
from pathlib import Path

from flask import Blueprint

from .state import app_state

# Define the blueprint
core_bp = Blueprint(
    'core',
    __name__,
    template_folder='templates',  # Path to templates specific to this blueprint
    static_folder='static',        # Path to static files specific to this blueprint
    static_url_path='/core/static' # URL prefix for static files
)

# Import routes (this ensures routes are registered with the blueprint)
from . import routes

# get the root path of the project and create the necessary directories
def get_project_root():
    # Try to locate the directory of the main script
    try:
        main_script = sys.modules['__main__'].__file__
        return os.path.abspath(os.path.dirname(main_script))
    except AttributeError:
        # Fallback to current working directory if __file__ is not available
        return os.getcwd()

base_path = get_project_root()
paths = {
    "screenshots": os.path.join(base_path, "screenshots"),
    "models": os.path.join(base_path, "models"),
    "user_components": os.path.join(base_path, "user_components"),
}

# Ensure directories exist
for path in paths.values():
    os.makedirs(path, exist_ok=True)

app_state.base_path = base_path
app_state.screenshot_folder = paths["screenshots"]
app_state.model_directory = paths['models']
app_state.user_components_directory = paths['user_components']

# TODO add functionality to select the default model (would prefer to not loading anything by default)
app_state.current_model = "OW2_new"
from .game_manager import game_manager
game_manager.screenshot_folder = app_state.screenshot_folder
game_manager.load_model(app_state.current_model)