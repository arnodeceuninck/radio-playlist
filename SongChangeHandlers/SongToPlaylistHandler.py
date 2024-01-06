import SongChangeHandlers.SongChangeHandler as SongChangeHandler

class SongToPlaylistHandler(SongChangeHandler):
    def __init__(self):
        super().__init__()

    def on_new_song(self, song):
        print("SongToPlaylistHandler started")
        print("SongToPlaylistHandler: Song added to playlist")