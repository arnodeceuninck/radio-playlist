from dotenv import load_dotenv
import os

from PlaylistBuilders.SpotifyPlaylistBuilder import SpotifyPlaylistBuilder
from SongChangeDetectors.VRTSongChangeDetector.VRTSongChangeDetector import VRTSongChangeDetector

# from SongChangeHandlers.SongToPlaylistHandler import SongToPlaylistHandler

class RadioPlaylistBuilder:
    def __init__(self):
        pass

    def start(self):
        print("RadioPlaylistBuilder started")
        playlist_builder = SpotifyPlaylistBuilder(playlist_name="MNM Hits - Live")
        song_change_detector = VRTSongChangeDetector(
                                    radio="mnmhits",
                                    change_handler=playlist_builder.add_song
                                )
        song_change_detector.start()

if __name__ == '__main__':
    load_dotenv() # Load environment variables from .env file

    radio_playlist_builder = RadioPlaylistBuilder()
    radio_playlist_builder.start()
