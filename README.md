# Game Statistics Tracker

A flexible, modular application for tracking, analyzing, and visualizing in-game statistics by processing screenshots. This tool enables you to capture screenshots, extract relevant data, and create custom logic or visualizations by implementing your own classes and UI components to suit your needs.

## Key Features

- **Screenshot Processing**  
  Automatically captures and processes game screenshots.

- **Custom Predictors**  
  Replace or extend the default prediction logic by supplying a custom class that implements `PredictorInterface`.

- **Custom Event Handlers**  
  Plug in your own class for handling and processing game events by implementing `EventsHandlerInterface`.

- **Modular Architecture**  
  Add new models or HTML elements without modifying core functionality. Simply place your custom scripts under the designated model directory, and `GameManager` will handle the rest.

## Getting Started

1. **Clone the Repository**  
   Clone this repository to your local machine.

2. **Install Dependencies**  
   Install the required Python dependencies. For example:
   ```bash
   pip install -r requirements.txt

3. **Run the Program**
   ```bash
   python main.py

4. **Visit the Application in a Browser**
   ```bash
   localhost:5000/

5. **Customize for Your Needs**

   Visit https://github.com/krpouncy/OWTracker for an example program that tracks OW games.
   
## Things to Keep in Mind:
- Currently, only the inputs `TAB` on PC and `Back Button` for Xbox are registered as screenshot buttons. 
- The Xbox controller is the default input at start-up.
- The application only takes screenshots of the primary monitor.

## TO-DO

### **Features to Add**
- **More Detailed Documentation**
  - Create more examples of how WatchStats could be used for different projects.
  - Explanation of creating the `predictor.py`, which extends `UserPredictor` and `events_handler.py`, which extends `UserEventsHandler`. More details can be found in the `models\__init__.py` file.
  
- **Model Selection:**
  - Allow the user to choose from different model directories dynamically (currently, it only selects the first discovered model).
  - Implement a search/filter mechanism for easier navigation between models.

- **UI Customization:**
  - Enable users to disable or hide specific UI elements based on their preferences.
  - Provide customization options for themes, including colors, fonts, and layouts.
  - Allow for uploading custom backgrounds or selecting from predefined options.

- **Expanded Functionality:**
  - Introduce more actions beyond screenshots, such as:
    - Real-time video recording.
    - Data export (e.g., CSV, JSON).
    - Annotations or notes for specific game events.
  - Add a **game browser** to view and manage recorded screenshots:
    - Include sorting, filtering, and tagging options for screenshots.
    - Provide a thumbnail preview for quick access.
