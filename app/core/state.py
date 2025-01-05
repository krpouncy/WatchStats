class AppState:
    input_type = "Controller"  # Default to "Keyboard"
    game_progress = []
    base_path = None
    screenshot_folder = None
    model_directory = None
    user_components_directory = None
    rules_df = None

# Singleton instance
app_state = AppState()