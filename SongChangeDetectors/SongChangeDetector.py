import logging

"""
Listens to the radio and triggers an event when a new song starts.
"""
class SongChangeDetector:
    def __init__(self, change_handler=None):
        self.change_handler = None
        if change_handler is not None:
            self.update_change_handler(change_handler)
        

    def start(self):
        logging.info("SongChangeDetector started")

    def update_change_handler(self, change_handler):
        assert change_handler is not None, "change_handler cannot be None"
        assert callable(change_handler), "change_handler must be callable"
        self.change_handler = change_handler