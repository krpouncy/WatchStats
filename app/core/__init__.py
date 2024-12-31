import os

from flask import Blueprint

from app.core.state import app_state

# Define the blueprint
core_bp = Blueprint(
    'core',
    __name__,
    template_folder='templates',  # Path to templates specific to this blueprint
    static_folder='static',        # Path to static files specific to this blueprint
    static_url_path='/core/static' # URL prefix for static files
)

# Import routes (this ensures routes are registered with the blueprint)
from app.core import routes

# Create necessary directories if they don't exist
def create_required_folders(folders=None):
    """Create necessary directories if they don't exist."""
    if folders is None:
        return {}

    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\..\\'))
    paths = {}

    for folder in folders:
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")
        paths[folder] = folder_path
    return paths

folder_paths = create_required_folders(folders=['screenshots', 'models'])
SCREENSHOT_PATH, MODEL_PATH = folder_paths['screenshots'], folder_paths['models']

app_state.screenshot_folder = SCREENSHOT_PATH
print(f"Screenshot path: {SCREENSHOT_PATH}")

app_state.model_path = os.path.join(MODEL_PATH, "latest_model.pth")