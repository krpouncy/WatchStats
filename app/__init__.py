# app/__init__.py

import sys
import os
from pathlib import Path
from flask import Flask
from flask_socketio import SocketIO

# needs to be initalized before importing the app.core modules
socketio = SocketIO()

from app.core.state import app_state
from app.core.game_manager import game_manager


# get the root path of the project and create the necessary directories
def get_project_root():
    """Get the root path of the project."""
    try:
        main_script = sys.modules['__main__'].__file__
        return os.path.abspath(os.path.dirname(main_script))
    except AttributeError:
        # Fallback to current working directory if __file__ is not available
        return os.getcwd()


def create_directories(dir_names):
    """Create directories with the given names in the project root."""
    base_path = get_project_root()  # Get the root path of the project
    paths = {dir_name: os.path.join(base_path, dir_name) for dir_name in dir_names}
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths


def setup_app_state():
    """Set up the app state with the necessary paths."""
    # set the base path of the project
    app_state.base_path = get_project_root()

    # Create the necessary directories
    paths = create_directories(['screenshots', 'models', 'user_components'])

    # Set the paths in the app state
    app_state.screenshot_folder = paths["screenshots"]
    app_state.model_directory = paths['models']
    app_state.user_components_directory = paths['user_components']


def get_available_models():
    """Get the list of available models in the model directory"""
    return [d for d in Path(app_state.model_directory).iterdir() if
            d.is_dir() and not d.name.startswith('.') and '__' not in d.name]


def setup_model():
    """Load the first available model in the model directory."""
    available_models = get_available_models()
    print("Model directories found:", [d.name for d in available_models])
    if available_models:
        app_state.current_model = available_models[0].name
    else:
        app_state.current_model = None  # Explicitly set to None if no models are found
    game_manager.load_model(app_state.current_model)

def create_app(config_name='default'):
    app = Flask(__name__, static_folder='static')

    # Load configuration
    if config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DefaultConfig')

    app.config['SECRET_KEY'] = 'your-secret-key'  # TODO: Change this to a random key

    socketio.init_app(app, async_mode='eventlet')

    from app.core import core_bp

    setup_app_state()
    setup_model()

    app.register_blueprint(core_bp, url_prefix='/')

    return app
