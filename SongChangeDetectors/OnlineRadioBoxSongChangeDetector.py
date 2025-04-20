import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import logging
from SongChangeDetectors.HtmlSongChangeDetector import SimpleSongPlay, HtmlSongChangeDetector

class OnlineRadioBoxSongChangeDetector(HtmlSongChangeDetector):
    def __init__(self, change_handler, radio_name, max_songs=10):
        logging.info(f"Creating OnlineRadioBoxSongChangeDetector for {radio_name}")
        super().__init__(change_handler, max_songs)
        self.radio_name = radio_name
        country, title = radio_name.split(".")
        self.radio_url = f"https://onlineradiobox.com/{country}/{title}/playlist/"

    def query_songs(self):
        response = requests.get(self.radio_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", attrs={"class": "tablelist-schedule"})
        rows = table.find_all("tr")

        songs = []
        for row in rows:
            cols = row.find_all("td")
            time = cols[0].find("span").text
            song = cols[1].find("a").text if cols[1].find("a") else cols[1].text
            if song == "Ad break\n\t" or " - " not in song:
                continue

            splitted = song.split(" - ")
            artist = splitted[0]
            title = splitted[-1]

            if artist in ["MNM hits", "MNM", "Radio 1"]:
                continue

            simple_song_play = SimpleSongPlay()
            simple_song_play.title = title.strip()
            simple_song_play.artist = artist.strip()

            if time in ["En direct", "Live"]:
                time_parsed = datetime.now()
            else:
                time_parsed = datetime.strptime(time, "%H:%M")
                time_parsed = datetime.now().replace(hour=time_parsed.hour, minute=time_parsed.minute, second=0, microsecond=0)
            simple_song_play.start_time = time_parsed

            songs.append(simple_song_play)

        return songs
