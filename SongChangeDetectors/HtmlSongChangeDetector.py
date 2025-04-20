import os
import time
import requests
import util
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

import Database.Util
from Database import Song, session, RadioSong
from SongChangeDetectors.SongChangeDetector import SongChangeDetector

class SimpleSongPlay:
    title = None
    artist = None
    start_time = None

    # compare a SimpleSongPlay object with a song object
    def __eq__(self, other):
        return self.title == other.song.title and self.artist == other.song.artist


class HtmlSongChangeDetector(SongChangeDetector):
    def __init__(self, change_handler, radio_name, max_songs=10):
        logging.info("Creating HtmlSongChangeDetector")
        super().__init__(change_handler)
        self.max_songs = max_songs
        self.radio_name = radio_name

    def start(self):
        logging.info("SongChangeDetector started")
        while True:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(self.handle_new_songs)
                try:
                    # Wait for handle_new_songs() to complete with a 60-minute timeout
                    future.result(timeout=60 * 60)
                except TimeoutError:
                    logging.warning("handle_new_songs timed out after 60 minutes")
                    future.cancel()
            time.sleep(60)

    def handle_new_songs(self):
        logging.info("Checking for new songs")
        new_songs = self.query_songs()
        og_count = len(new_songs)
        new_songs = self.filter_new_songs(new_songs)
        logging.info(f"Found {len(new_songs)} new songs out of {og_count} songs")
        new_songs = sorted(new_songs, key=lambda song: song.start_time)
        if len(new_songs) > self.max_songs:
            new_songs = new_songs[:-self.max_songs]
        for new_song in new_songs:
            logging.info(f"New song: {new_song.title} - {new_song.artist}")
            radio_song = self.create_db_radio_song(new_song)
            self.change_handler(radio_song)
            # raise Exception("Stop here for debugging purposes")

    def create_db_radio_song(self, simple_song):
        song = Database.Util.get_or_create_song(simple_song.title, simple_song.artist)
        radio = Database.Util.get_or_create_radio(name=self.radio_name)
        radio_song = RadioSong(radio_id=radio.id, song_id=song.id, start_time=simple_song.start_time)

        session.add(radio_song)
        session.commit()
        logging.info(f"Added new song to database: {simple_song.title} - {simple_song.artist}")

        return radio_song

    def filter_new_songs(self, songs):
        last_radio_song = self.get_last_submitted_radio_song()
        if last_radio_song is not None:
            songs = [song for song in songs if song.start_time > last_radio_song.start_time and song != last_radio_song]
        return songs

    def query_songs(self):
        raise NotImplementedError("Subclasses must implement query_songs")

    def get_last_submitted_radio_song(self):
        return Database.Util.get_last_radio_song(self.radio_name)
