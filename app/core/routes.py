# app/core/routes.py

import json
import os

from flask import render_template, request, jsonify, send_from_directory

from app import socketio
from models import HandlerEvent
from . import core_bp
from .game_manager import game_manager
from .state import app_state


@core_bp.route('/')
def dashboard():
    components = []
    base_dir = app_state.user_components_directory

    # Iterate over top-level directories (e.g., games or groups)
    for user_dir in os.listdir(base_dir):
        user_path = os.path.join(base_dir, user_dir)
        if os.path.isdir(user_path):
            # Iterate over components within each user directory
            for component_dir in os.listdir(user_path):
                component_path = os.path.join(user_path, component_dir)
                if os.path.isdir(component_path):
                    # Define file paths
                    html_path = os.path.join(component_path, 'component.html')
                    js_path = os.path.join(component_path, 'component.js')
                    config_path = os.path.join(component_path, 'config.json')

                    # Read component data
                    component = {
                        'id': f"{user_dir}_{component_dir}",  # Unique identifier
                        'html': open(html_path).read() if os.path.exists(html_path) else '',
                        'js': open(js_path).read() if os.path.exists(js_path) else '',
                        'config': json.load(open(config_path)) if os.path.exists(config_path) else {},
                    }
                    components.append(component)

                    # user_dir as parent in config
                    component['config']['parent'] = user_dir

    # Sort components by 'order' if specified in their config.json
    components.sort(key=lambda x: x['config'].get('order', 0))
    return render_template('dashboard.html', components=components)


@core_bp.route('/about')
def about():
    return render_template('about.html')


# Routes for programmable events
@core_bp.route('/load')
def load_route():
    # Emit a page load event to the client
    game_manager.events_handler.handle_event(socketio, HandlerEvent.PAGE_LOAD, payload=None)
    return jsonify({'status': 'success'})


@core_bp.route('/set-input', methods=['POST'])
def set_input():
    """Set the input type dynamically (Keyboard or Controller)."""
    new_input_type = request.json.get('input_type')
    if new_input_type in ["PC", "Controller"]:
        app_state.input_type = new_input_type
        return jsonify({"status": "success", "input_type": app_state.input_type})
    return jsonify({"status": "error", "message": "Invalid input type"}), 400


@core_bp.route('/get-input', methods=['GET'])
def get_input():
    """Get the current input type."""
    return jsonify({"input_type": app_state.input_type})


@core_bp.route('/reset-input', methods=['POST'])
def reset_input():
    """Reset the input type."""
    app_state.input_type = None
    response = jsonify({'status': 'success'})
    response.delete_cookie('input_type')
    return response


@core_bp.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    """Serve a screenshot file."""
    screenshot_folder = os.path.abspath(game_manager.screenshot_folder)
    return send_from_directory(screenshot_folder, filename)


@core_bp.route('/api/screenshots')
def get_screenshots():
    """Get a list of screenshots from screenshot folder."""
    screenshot_folder = game_manager.screenshot_folder
    if not os.path.exists(screenshot_folder):
        return jsonify({'screenshots': []})

    files = [f for f in os.listdir(screenshot_folder) if f.lower().endswith('.png')]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(screenshot_folder, x)))

    return jsonify({'screenshots': files})


@core_bp.route('/set-game-outcome', methods=['POST'])
def set_game_outcome():
    """Set the outcome of the game."""
    game_result = request.json.get('outcome')
    if not game_result:
        return jsonify({'status': 'error', 'message': 'No game outcome provided'}), 400

    folder = game_manager.move_screenshots_to_folder(game_result)
    print(f"Moved screenshots to {folder}")

    game_manager.events_handler.handle_event(socketio, HandlerEvent.GAME_OUTCOME_SET, {'outcome': game_result, 'folder': folder})

    return jsonify({'status': 'success', 'folder': folder})


@core_bp.route('/save_layout', methods=['POST'])
def save_layout():
    data = request.json
    layout = data.get('layout', [])
    # Update each component's configuration file
    for item in layout:
        folder_name = item['parent']
        component_name = item['id'].replace(f"{folder_name}_", "")
        component_dir = os.path.join(app_state.user_components_directory, folder_name, component_name)
        config_path = os.path.join(str(component_dir), 'config.json')
        print(component_dir, '\n', config_path)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            config.update({
                'x': item['x'],
                'y': item['y'],
                'width': item['width'],
                'height': item['height']
            })
            with open(config_path, 'w') as f:
                json.dump(config, f)

    return jsonify({'status': 'success'})

# TODO GET THIS WORKING AND DETERMINE IF SECURITY IS NECESSARY
# @core_bp.after_request
# def apply_csp(response):
#     # response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self';"
#     # update to Content-Security-Policy: default-src 'self'; style-src 'self' https://cdnjs.cloudflare.com
#     # TODO remove unsafe-inline and add nonce for inline scripts
#     response.headers['Content-Security-Policy'] = (
#         "default-src 'self'; "
#         "script-src 'self' https://cdn.jsdelivr.net https://cdn.socket.io; "
#         "style-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net 'unsafe-inline'; "
#     )
#     return response
