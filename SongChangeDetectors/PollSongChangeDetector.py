from SongChangeDetectors.SongChangeDetector import SongChangeDetector
class PollSongChangeDetector(SongChangeDetector):
    def __init__(self, poll_interval=1):
        super().__init__()
        self.poll_interval = poll_interval
        self.last_song = None

    def detect_change(self):
        current_song = self.get_current_song()
        if current_song != self.last_song:
            self.last_song = current_song
            return True
        return False

    def get_current_song(self):
        return None