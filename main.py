import time
import os
from dotenv import load_dotenv
import argparse
import logging

from concurrent.futures import ThreadPoolExecutor, TimeoutError

from PlaylistBuilders.SpotifyPlaylistBuilder import SpotifyPlaylistBuilder
from SongChangeDetectors.HtmlSongChangeDetector import HtmlSongChangeDetector
from SongChangeDetectors.QmusicSongChangeDetector import QMusicBelgiumSongChangeDetector
from SongChangeDetectors.VRTSongChangeDetector.VRTSongChangeDetector import VRTSongChangeDetector
from SongChangeDetectors.OnlineRadioBoxSongChangeDetector import OnlineRadioBoxSongChangeDetector
from cache_loader import load_cache_from_env

def parse_radios_from_env():
    """
    Parse radio configuration from RADIOS environment variable.
    
    Format: comma-separated list of radio identifiers (e.g., "be.mnmhits,be.mnm,be.studiobrussel")
    Each identifier will be converted to a radio name: "be.mnmhits" -> "MNM Hits - Live Radio"
    
    Returns:
        dict: Dictionary mapping radio names to identifiers, or None if env var not set
    """
    radios_env = os.getenv('RADIOS')
    if not radios_env:
        return None
    
    radios = {}
    radio_identifiers = [r.strip() for r in radios_env.split(',') if r.strip()]
    
    # Map identifiers to human-readable names
    identifier_to_name = {
        'be.mnmhits': 'MNM Hits - Live Radio',
        'be.mnm': 'MNM - Live Radio',
        'be.studiobrussel': 'Studio Brussel (StuBru) - Live Radio',
        'be.qmusic': 'Qmusic - Live Radio',
        'be.willy': 'Willy Radio - Live Radio',
        'be.joe': 'JOE - Live Radio',
        'be.r1': 'Radio 1 - Live Radio',
        'be.ketnet': 'Ketnet Hits - Live Radio',
        'be.studiobrusseldetijdloze': 'StuBru - De Tijdloze - Live Radio',
        'be.studiobrusselbruut': 'StuBru - Bruut - Live Radio',
        'be.topretroarena': 'TOPradio - TOPretroarena - Live Radio',
        'be.topselection': 'TOPradio - TOPtechno - Live Radio',
        'be.topradio': 'TOPradio - Live Radio',
        'be.studiobrusselikluisterbelgisch': 'StuBru - Ik Luister Belgisch - Live Radio',
        'be.studiobrusseluntz': 'StuBru - UNTZ - Live Radio',
    }
    
    for identifier in radio_identifiers:
        # Use predefined name if available, otherwise create a generic name
        name = identifier_to_name.get(identifier, f"{identifier} - Live Radio")
        radios[name] = identifier
    
    logging.info(f"Loaded {len(radios)} radios from RADIOS environment variable")
    return radios

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

        poll_interval_s = 60 # note that the actual polling will be longer due to the time taken to process each radio
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
    load_cache_from_env()
    
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

    playlist_builder = SpotifyPlaylistBuilder()

    # Try to load radios from environment variable, fall back to default configuration
    radios = parse_radios_from_env()
    
    if radios is None:
        logging.info("No RADIOS environment variable found, using default configuration")
        radios = {
            "TST MNM - Live": "be.mnm",
        }

    radio_playlist_builder = MultiRadioPlaylistBuilder(radios=radios, playlist_builder=playlist_builder)
    radio_playlist_builder.start()
