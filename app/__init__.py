# app/__init__.py
import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()  # We'll configure async_mode below


def create_app():
    # Disable or set a valid global static_folder, if you prefer blueprint-based static
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = 'your-secret-key'

    socketio.init_app(app, async_mode='eventlet')

    # Register your blueprint(s)
    from app.core import core_bp
    app.register_blueprint(core_bp, url_prefix='/')

    return app
