class AppState:
    """
    Application state class to store global variables and state datas
    """
    input_type = "Controller"  # Default to "Keyboard"
    state_data = {} # Store state data or global variables
    base_path = None
    screenshot_folder = None
    model_directory = None
    user_components_directory = None
    rules_df = None

# Singleton instance
app_state = AppState()