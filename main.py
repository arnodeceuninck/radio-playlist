from SongChangeDetectors.SongChangeDetector import SongChangeDetector
from SongChangeHandlers.SongToPlaylistHandler import SongToPlaylistHandler

class RadioPlaylistBuilder:
    def __init__(self):
        pass

    def start(self):
        print("RadioPlaylistBuilder started")
        song_change_detector = SongChangeDetector()
        song_change_detector.change_handler = SongToPlaylistHandler()
        song_change_detector.start()

if __name__ == '__main__':
    radio_playlist_builder = RadioPlaylistBuilder()
    radio_playlist_builder.start()
