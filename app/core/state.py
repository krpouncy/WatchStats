class AppState:
    input_type = "PC"  # Default to "Keyboard"
    game_progress = []
    screenshot_folder = None
    model_path = None # TODO consider moving to private location
    rules_df = None

# Singleton instance
app_state = AppState()