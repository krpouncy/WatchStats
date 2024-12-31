class AppState:
    input_type = "PC"  # Default to "Keyboard"
    game_progress = []
    input_type = None
    screenshot_folder = 'screenshots' # TODO handle NONE cases (rename to None and adjust other code)
    model_path = 'models' # TODO handle NONE cases (rename to None and adjust other code), also consider moving to private loc

# Singleton instance
app_state = AppState()