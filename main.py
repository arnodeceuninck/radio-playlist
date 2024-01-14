from dotenv import load_dotenv
import argparse

from PlaylistBuilders.SpotifyPlaylistBuilder import SpotifyPlaylistBuilder
from SongChangeDetectors.VRTSongChangeDetector.VRTSongChangeDetector import VRTSongChangeDetector


class RadioPlaylistBuilder:
    def __init__(self, playlist_name, radio):
        self.playlist_name = playlist_name
        self.radio = radio

    def start(self):
        print(f"RadioPlaylistBuilder started for {self.radio}")
        playlist_builder = SpotifyPlaylistBuilder(playlist_name=self.playlist_name)
        song_change_detector = VRTSongChangeDetector(
            radio=self.radio,
            change_handler=playlist_builder.add_song
        )
        song_change_detector.start()

if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file

    parser = argparse.ArgumentParser(description='Get a spotify playlist with the same songs as currently live playing on the radio.')
    parser.add_argument('--playlist', type=str, default='MNM Hits - Live', help='Name of the playlist')
    parser.add_argument('--radio', type=str, default='mnmhits', help='Name of the radio (mnm, mnmhits or stubru)')

    args = parser.parse_args()

    # radio_playlist_builder = RadioPlaylistBuilder(playlist_name=args.playlist, radio=args.radio)
    radio_playlist_builder = RadioPlaylistBuilder(playlist_name='Studio Brussel (StuBru) - Live', radio='stubru')
    radio_playlist_builder.start()
