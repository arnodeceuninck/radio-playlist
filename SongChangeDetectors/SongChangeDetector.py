"""
Listens to the radio and triggers an event when a new song starts.
"""
class SongChangeDetector:
    def __init__(self):
        self.change_handler = None

    def start(self):
        print("SongChangeDetector started")