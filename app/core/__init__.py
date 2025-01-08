import os
import sys
from pathlib import Path

from flask import Blueprint

from .game_manager import game_manager
from .state import app_state

# Define the blueprint
core_bp = Blueprint(
    'core',
    __name__,
    template_folder='templates',  # Path to templates specific to this blueprint
    static_folder='static',  # Path to static files specific to this blueprint
    static_url_path='/core/static'  # URL prefix for static files
)
from . import routes  # Import the routes module to register the routes [import after core_bp]