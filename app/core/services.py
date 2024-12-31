# app/core/services.py

from flask_socketio import SocketIO
from .game_manager import game_manager
from .classification import get_stats_and_details, prediction_model
from .state import game_progress  # if you keep global progress here
# from app import socketio

# socketio = SocketIO()  # If you haven't already imported a global socketio

# def process_screenshot():
    # filename = game_manager.take_screenshot()
    #
    # socketio.emit('screenshot_taken', {'filename': filename})
    # socketio.emit('show_loading_overlay')
    # details = get_stats_and_details(filename)
    # print("Details: ", details)
    # socketio.emit('hide_loading_overlay')

    # if details is not None:
    #     stats, game_details = details
    #     prob = prediction_model.predict_probability(stats, game_details)
    #
    #     if prob is not None:
    #         game_progress.append(prob)
    #         socketio.emit('update_chart', {'win_probability': prob})
    #         print(f"Updated Win Probability: {prob}")
    #
    #     # _, team_composition, team_status = game_details
    #     # update_player_status(team_status, team_composition)
    #     #
    #     # # save the current team composition
    #     # socketio.emit('update_team_composition', {'my_team': my_team_players})
    #     else:
    #         game_manager.current_screenshots.pop()
    # else:
    #     game_manager.current_screenshots.pop()
