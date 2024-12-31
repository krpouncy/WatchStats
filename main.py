# main.py
from app import create_app, socketio
from app.core.input_listener import input_listener

def main():
    app = create_app()

    # TODO FOR DEBUGGING ONLY
    # with app.app_context():
    #     for rule in app.url_map.iter_rules():
    #         print(f"{rule.endpoint}: {rule}")

    # Start the input listener in the background
    socketio.start_background_task(input_listener)

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True, # TODO don't forget to disable
        use_reloader=False
    )

if __name__ == "__main__":
    main()
