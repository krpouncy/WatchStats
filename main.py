# main.py
from app import create_app, socketio
from app.core.input_listener import input_listener

def main():
    app = create_app()

    # Start the input listener in the background
    socketio.start_background_task(input_listener)

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )

if __name__ == "__main__":
    main()
