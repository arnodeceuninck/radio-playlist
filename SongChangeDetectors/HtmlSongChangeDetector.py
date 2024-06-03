import os
import time
import requests
import util
from datetime import datetime
from bs4 import BeautifulSoup

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
    def __init__(self, change_handler, radio_name):
        super().__init__(change_handler)
        self.radio_name = radio_name

    def start(self):
        print("SongChangeDetector started")
        while True:
            self.handle_new_songs()
            time.sleep(60)


    def handle_new_songs(self):
        new_songs = self.query_songs()
        new_songs = self.filter_new_songs(new_songs)
        new_songs = sorted(new_songs, key=lambda song: song.start_time)
        for new_song in new_songs:
            print(f"New song: {new_song.title} - {new_song.artist}")
            radio_song = self.create_db_radio_song(new_song)
            self.change_handler(radio_song)
            # raise Exception("Stop here for debugging purposes")

    def create_db_radio_song(self, simple_song):
        song = Database.Util.get_or_create_song(simple_song.title, simple_song.artist)
        radio = Database.Util.get_or_create_radio(name=self.radio_name)
        radio_song = RadioSong(radio_id=radio.id, song_id=song.id, start_time=simple_song.start_time)

        session.add(radio_song)
        session.commit()

        return radio_song

    def filter_new_songs(self, songs):
        last_radio_song = self.get_last_submitted_radio_song()
        if last_radio_song is not None:
            songs = [song for song in songs if song.start_time > last_radio_song.start_time and song != last_radio_song]
        return songs


    def query_songs(self):
        url = "https://onlineradiobox.com/be/willy/playlist/?cs=be.willy"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", attrs={"class": "tablelist-schedule"})
        rows = table.find_all("tr")

        # <tr>
        # 	<td class="tablelist-schedule__time"><span class="time--schedule">21:07</span></td>
        # 	<td class="track_history_item"><a href="/track/8597003/" class="ajax">FOO FIGHTERS - Times Like These</a>
        # 	</td>
        # </tr>

        songs = []
        for row in rows:
            cols = row.find_all("td")
            time = cols[0].find("span").text
            song = cols[1].find("a").text if cols[1].find("a") else cols[1].text
            if song == "Ad break\n\t":
                continue
            artist, title = map(str.strip, song.split(" - "))

            # create a SimpleSongPlay object
            simple_song_play = SimpleSongPlay()
            simple_song_play.title = title
            simple_song_play.artist = artist

            # change time format to today's date at the given time
            if time in ["En direct", "Live"]:
                time_parsed = datetime.now()
            else:
                time_parsed = datetime.strptime(time, "%H:%M")
                time_parsed = datetime.now().replace(hour=time_parsed.hour, minute=time_parsed.minute, second=0, microsecond=0)
            simple_song_play.start_time = time_parsed

            songs.append(simple_song_play)

        return songs

    def get_last_submitted_radio_song(self):
        return Database.Util.get_last_radio_song(self.radio_name)
