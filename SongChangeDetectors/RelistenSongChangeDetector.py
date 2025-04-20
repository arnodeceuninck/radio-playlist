import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from SongChangeDetectors.HtmlSongChangeDetector import SimpleSongPlay, HtmlSongChangeDetector

class RelistenSongChangeDetector(HtmlSongChangeDetector):
    # https://www.relisten.be/playlists/qmusic
    def __init__(self, change_handler, playlist_url, max_songs=10):
        logging.info(f"Creating RelistenSongChangeDetector for {playlist_url}")
        super().__init__(change_handler, max_songs)
        self.radio_url = playlist_url

    def query_songs(self):
        response = requests.get(self.radio_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        schedule_div = soup.find("div", class_="playlist-wrap")
        raise NotImplementedError("Not yet implemented") # at the time of testing, I got a 508 (resource limit is reached)

if __name__ == "__main__":
    # Example usage
    def change_handler(radio_song):
        print(f"New song: {radio_song.song.title} - {radio_song.song.artist}")

    detector = RelistenSongChangeDetector(change_handler, "https://www.relisten.be/playlists/qmusic")
    detector.handle_new_songs()