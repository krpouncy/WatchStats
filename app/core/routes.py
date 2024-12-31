# app/core/routes.py

import os

from app import socketio
from flask import render_template, request, jsonify, send_from_directory
from . import core_bp
from app.core.game_manager import game_manager
from app.core.state import app_state

@core_bp.route('/')
def index():
    """ Renders the core index or main page (no premium data). """
    # start_input_listener()
    return render_template('core_index.html')  # This could be your core HTML template

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
    global input_type
    input_type = None
    response = jsonify({'status': 'success'})
    response.delete_cookie('input_type')
    return response

@core_bp.route('/api/chart-data')
def get_chart_data():
    return jsonify({
        "labels": [f"Event {i+1}" for i in range(len(game_progress))],
        "datasets": [{
            "label": "Win Probability",
            "data": [round(prob * 100, 1) for prob in game_progress],
            "backgroundColor": ["#4caf50" if prob > 0.5 else "#f44336" for prob in game_progress]
        }]
    })

@core_bp.route('/reset-chart', methods=['POST'])
def reset_chart():
    global game_progress
    game_progress = []
    socketio.emit('reset_chart')
    return jsonify({'status': 'success'})

# @core_bp.route('/take-screenshot', methods=['POST'])
# def manual_screenshot():
#     # process_screenshot() #TODO - call the function
#     print("Manual screenshot taken")
#     return jsonify({'status': 'success'})

@core_bp.route('/screenshots/<path:filename>')
def serve_screenshot(filename):
    screenshot_folder = os.path.abspath(game_manager.screenshot_folder)
    return send_from_directory(screenshot_folder, filename)

@core_bp.route('/api/screenshots')
def get_screenshots():
    screenshot_folder = game_manager.screenshot_folder
    if not os.path.exists(screenshot_folder):
        return jsonify({'screenshots': []})

    files = [f for f in os.listdir(screenshot_folder) if f.lower().endswith('.png')]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(screenshot_folder, x)))

    return jsonify({'screenshots': files})

@core_bp.route('/set-game-outcome', methods=['POST'])
def set_game_outcome():
    game_result = request.json.get('outcome')
    if not game_result:
        return jsonify({'status': 'error', 'message': 'No game outcome provided'}), 400

    folder = game_manager.move_screenshots_to_folder(game_result)
    print(f"Moved screenshots to {folder}")

    socketio.emit('game_outcome_set', {'outcome': game_result, 'folder': folder})
    return jsonify({'status': 'success', 'folder': folder})