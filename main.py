import time
from dotenv import load_dotenv
import argparse
import logging

from PlaylistBuilders.SpotifyPlaylistBuilder import SpotifyPlaylistBuilder
from SongChangeDetectors.HtmlSongChangeDetector import HtmlSongChangeDetector
from SongChangeDetectors.VRTSongChangeDetector.VRTSongChangeDetector import VRTSongChangeDetector

class MultiRadioPlaylistBuilder:
    def __init__(self, radios):
        self.radios = radios
        self.change_detectors = {}

    def start(self):
        logging.info(f"MultiRadioPlaylistBuilder started")

        playlist_builder = SpotifyPlaylistBuilder()

        for radio_name, radio_id in self.radios.items():
            song_change_detector = HtmlSongChangeDetector(
                change_handler=playlist_builder.add_song,
                radio_name=radio_id,
                max_songs=120
            )

            self.change_detectors[radio_name] = song_change_detector

        poll_interval_s = 90
        poll_interval_per_radio_s = poll_interval_s / len(self.radios)

        while True:
            for radio_name, song_change_detector in self.change_detectors.items():

                playlist_builder.switch_playlist(radio_name)
                song_change_detector.update_change_handler(playlist_builder.add_song)
                
                song_change_detector.handle_new_songs()
                
                time.sleep(poll_interval_per_radio_s)

if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    radios = {
        "MNM Hits - Live Radio": "be.mnmhits",
        "MNM - Live Radio": "be.mnm",
        "Studio Brussel (StuBru) - Live Radio": "be.studiobrussel",
        "Willy Radio - Live Radio": "be.willy",
        "JOE - Live Radio": "be.joe",
        "Radio 1 - Live Radio": "be.r1",
        "Ketnet Hits - Live Radio": "be.ketnet",
        "Qmusic - Live Radio": "be.qmusic"
    }


    # radios = {
    #     "TST MNM - Live": "be.mnm",
    # }

    radio_playlist_builder = MultiRadioPlaylistBuilder(radios=radios)
    radio_playlist_builder.start()
