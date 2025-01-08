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
