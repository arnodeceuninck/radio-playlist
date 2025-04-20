import time
from dotenv import load_dotenv
import argparse
import logging

from concurrent.futures import ThreadPoolExecutor, TimeoutError

from PlaylistBuilders.SpotifyPlaylistBuilder import SpotifyPlaylistBuilder
from SongChangeDetectors.HtmlSongChangeDetector import HtmlSongChangeDetector
from SongChangeDetectors.QmusicSongChangeDetector import QMusicBelgiumSongChangeDetector
from SongChangeDetectors.VRTSongChangeDetector.VRTSongChangeDetector import VRTSongChangeDetector
from SongChangeDetectors.OnlineRadioBoxSongChangeDetector import OnlineRadioBoxSongChangeDetector

class MultiRadioPlaylistBuilder:
    def __init__(self, radios, playlist_builder):
        self.playlist_builder = playlist_builder
        self.radios = radios
        self.change_detectors = {}

    def start(self):
        logging.info(f"MultiRadioPlaylistBuilder started")

        for radio_name, radio_id in self.radios.items():
            if isinstance(radio_id, str):
                logging.info(f"Creating HtmlSongChangeDetector for {radio_name}")
                song_change_detector = OnlineRadioBoxSongChangeDetector(
                    change_handler=playlist_builder.add_song,
                    radio_name=radio_id,
                    max_songs=120
                )
            else:
                logging.info(f"Using provided SongChangeDetector for {radio_name}")
                song_change_detector = radio_id

            self.change_detectors[radio_name] = song_change_detector

        poll_interval_s = 10 # note that the actual polling will be longer due to the time taken to process each radio
        poll_interval_per_radio_s = poll_interval_s / len(self.radios)

        logging.info(f"Polling interval: {poll_interval_s} seconds")
        while True:
            for radio_name, song_change_detector in self.change_detectors.items():
                try:
                    logging.info(f"Processing {radio_name}")

                    playlist_builder.switch_playlist(radio_name)
                    song_change_detector.update_change_handler(playlist_builder.add_song)
                    
                    with ThreadPoolExecutor() as executor:
                        future = executor.submit(song_change_detector.handle_new_songs)
                        try:
                            # Wait for handle_new_songs() to complete with a 60-minute timeout
                            future.result(timeout=60 * 60)
                        except TimeoutError:
                            logging.warning("handle_new_songs timed out after 60 minutes")
                            # cancel the future if you want to ensure it doesn't run further
                            future.cancel()
                except Exception as e:
                    logging.exception(f"Error processing {radio_name}: {e}")

                
                time.sleep(poll_interval_per_radio_s)

if __name__ == '__main__':
    load_dotenv()  # Load environment variables from .env file

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    playlist_builder = SpotifyPlaylistBuilder()

    radios = {

        # Main
        "MNM Hits - Live Radio": "be.mnmhits",
        "MNM - Live Radio": "be.mnm",
        "Studio Brussel (StuBru) - Live Radio": "be.studiobrussel",
        # "Qmusic - Live Radio": "be.qmusic",
        "Qmusic - Live Radio": QMusicBelgiumSongChangeDetector(radio_name="Qmusic - Live Radio", change_handler=playlist_builder.add_song),
        # "Willy Radio - Live Radio": "be.willy", # Temporarily not available on https://onlineradiobox.com/be/willy/playlist/?cs=be.willy
        "Willy Radio - Live Radio": QMusicBelgiumSongChangeDetector(radio_name="Willy Radio - Live Radio", change_handler=playlist_builder.add_song, station_id="willy_be", base="api.willy.radio"),

        # Extra
        # "JOE - Live Radio": "be.joe",
        # "Radio 1 - Live Radio": "be.r1",
        # "Ketnet Hits - Live Radio": "be.ketnet",

        # Requested
        # "StuBru - De Tijdloze - Live Radio": "be.studiobrusseldetijdloze",
        # "StuBru - Bruut - Live Radio": "be.studiobrusselbruut",

        # "TOPradio - TOPretroarena - Live Radio": "be.topretroarena", # will have quite some incorrect ones because of multiple dj mix sets
        # "TOPradio - TOPtechno - Live Radio": "be.topselection", # somehow empty https://onlineradiobox.com/be/topselection/playlist/?cs=be.topselection
        # "TOPradio - Live Radio": "be.topradio", # also empty https://onlineradiobox.com/be/topradio/playlist/?cs=be.topselection

        # Those do not have any content on onlineradiobox
        # "StuBru - Ik Luister Belgisch - Live Radio": "be.studiobrusselikluisterbelgisch",
        # "StuBru - UNTZ - Live Radio": "be.studiobrusseluntz",
    }

    # radios = {
    #     "TST MNM - Live": QMusicBelgiumSongChangeDetector(radio_name="Qmusic - Live Radio", change_handler=playlist_builder.add_song),
    # }

    radio_playlist_builder = MultiRadioPlaylistBuilder(radios=radios, playlist_builder=playlist_builder)
    radio_playlist_builder.start()
