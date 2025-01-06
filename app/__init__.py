# app/__init__.py
# import eventlet
# eventlet.monkey_patch()
from flask import Flask
from flask_socketio import SocketIO

socketio = SocketIO()  # We'll configure async_mode below

def create_app(config_name='default'):
    app = Flask(__name__, static_folder='static')

    # Load configuration
    if config_name == 'testing':
        app.config.from_object('app.config.TestingConfig')
    else:
        app.config.from_object('app.config.DefaultConfig')

    app.config['SECRET_KEY'] = 'your-secret-key' # TODO: Change this to a random key

    socketio.init_app(app, async_mode='eventlet')

    from app.core import core_bp # import here to avoid circular imports
    app.register_blueprint(core_bp, url_prefix='/')

    return app
