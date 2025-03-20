from models import EventsHandlerInterface, HandlerEvent
import random

class UserEventsHandler(EventsHandlerInterface):
    def handle_event(self, socket_object, event_name, payload=None):
        """
        Handle the given event with the given payload.

        Current events:
            PAGE_LOAD - this is called when the html page loads
            GAME_DETAILS - this is called if details are returned (get_stats_and_details) after screenshot is taken
            GAME_PREDICTION - this is called after the predict_probability returns a value
            GAME_OUTCOME_SET - this is called when an outcome is set
        """
        if event_name == HandlerEvent.GAME_OUTCOME_SET and payload:
            socket_object.emit("game_end", payload['outcome'])