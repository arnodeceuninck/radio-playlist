"""
Listens to the radio and triggers an event when a new song starts.
"""
class SongChangeDetector:
    def __init__(self, change_handler):
        assert change_handler is not None, "change_handler cannot be None"
        assert callable(change_handler), "change_handler must be callable"
        self.change_handler = change_handler

    def start(self):
        print("SongChangeDetector started")