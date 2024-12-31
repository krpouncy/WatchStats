# main.py
from app import create_app, socketio
from app.core.input_listener import input_listener

def main():
    app = create_app()

    with app.app_context():
        for rule in app.url_map.iter_rules():
            print(f"{rule.endpoint}: {rule}")

    socketio.start_background_task(input_listener)

    # IMPORTANT: Run using socketio.run(...), not 'flask run'
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False # TODO determine if you still need this to avoid messing with threads because switched to eventlet
    )

if __name__ == "__main__":
    main()
