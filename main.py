from SongChangeDetectors.SongChangeDetector import SongChangeDetector
from SongChangeDetectors.VRTSongChangeDetector.VRTSongChangeDetector import VRTSongChangeDetector


# from SongChangeHandlers.SongToPlaylistHandler import SongToPlaylistHandler

def random_change_handler(new_songs):
    return 1

class RadioPlaylistBuilder:
    def __init__(self):
        pass

    def start(self):
        print("RadioPlaylistBuilder started")
        song_change_detector = VRTSongChangeDetector()
        # song_change_detector.change_handler = SongToPlaylistHandler()
        song_change_detector.change_handler = random_change_handler
        song_change_detector.start()

if __name__ == '__main__':
    radio_playlist_builder = RadioPlaylistBuilder()
    radio_playlist_builder.start()
