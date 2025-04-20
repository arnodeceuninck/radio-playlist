import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from SongChangeDetectors.HtmlSongChangeDetector import SimpleSongPlay, HtmlSongChangeDetector

class OnlineRadioBoxSongChangeDetector(HtmlSongChangeDetector):
    # https://radio-online-belgie.com/playlist/qmusic-playlist
    # TODO: Not yet working. Needs some javascript to get the final view. (and songs to be loaded from <scripts> tag, once final code is loaded)
    def __init__(self, change_handler, playlist_url, max_songs=10):
        logging.info(f"Creating RadioOnlineBelgieSongChangeDetector for {playlist_url}")
        super().__init__(change_handler, max_songs)
        self.radio_url = playlist_url

    def query_songs(self):
        response = requests.get(self.radio_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        schedule_div = soup.find("div", class_="playlist-wrap")
        if not schedule_div:
            return []
        song_entries = schedule_div.find_all("div", class_="playlist-item")

        songs = []
        for entry in song_entries:
            time_element = entry.find("span", class_="time")
            artist_element = entry.find("span", class_="artist")
            title_element = entry.find("span", class_="title")

            if not all([time_element, artist_element, title_element]):
                continue

            time_str = time_element.text.strip()
            artist = artist_element.text.strip()
            title = title_element.text.strip()

            if artist in ["MNM hits", "MNM", "Radio 1"]:
                continue

            simple_song_play = SimpleSongPlay()
            simple_song_play.title = title
            simple_song_play.artist = artist

            if time_str in ["En direct", "Live"]:
                simple_song_play.start_time = datetime.now().replace(second=0, microsecond=0)
            else:
                try:
                    time_parsed = datetime.strptime(time_str, "%H:%M")
                    simple_song_play.start_time = datetime.now().replace(hour=time_parsed.hour, minute=time_parsed.minute, second=0, microsecond=0)
                except ValueError:
                    continue  # Skip if time format is incorrect

            songs.append(simple_song_play)

        return songs

if __name__ == "__main__":
    # Example usage
    def change_handler(radio_song):
        print(f"New song: {radio_song.song.title} - {radio_song.song.artist}")

    detector = OnlineRadioBoxSongChangeDetector(change_handler, "https://radio-online-belgie.com/playlist/qmusic-playlist")
    detector.handle_new_songs()