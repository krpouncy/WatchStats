from models import EventsHandlerInterface

class UserEventsHandler(EventsHandlerInterface):
    def handle_event(self, socket_object, event_name, payload=None):
        """
        Handle the given event with the given payload.
        """
        pass