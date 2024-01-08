import os
import time
import requests
from datetime import datetime

import Database.Util
from Database import Song, session, RadioSong
from SongChangeDetectors.SongChangeDetector import SongChangeDetector

class VRTSongChangeDetector(SongChangeDetector):
    def __init__(self, radio, change_handler):
        super().__init__()
        assert change_handler is not None, "change_handler cannot be None"
        assert callable(change_handler), "change_handler must be callable"
        assert radio in ["mnmhits", "mnm", "stubru"], "Radio not supported"
        self.radio = radio

    def start(self):
        print("SongChangeDetector started")
        while True:
            self.handle_new_songs()
            time.sleep(60)


    def handle_new_songs(self):
        new_songs = self.query_songs()
        new_songs = self.filter_new_songs(new_songs)
        new_songs = sorted(new_songs, key=lambda song: song.radio_time)
        for new_song in new_songs:
            radio_song = self.create_db_radio_song(new_song)
            self.change_handler(radio_song)
            raise Exception("Stop here for debugging purposes")

    def create_db_radio_song(self, song):
        title = song["title"]
        artist = song["artist"]

        song = Database.Util.get_or_create_song(title, artist)
        radio = Database.Util.get_or_create_radio(name="MNM Hits")
        radio_song = RadioSong(radio=radio, song=song, start_time=song["startDate"], end_time=song["endDate"])

        session.add(radio_song)
        session.commit()

        return radio_song

    def filter_new_songs(self, songs):
        last_radio_song = self.get_last_submitted_radio_song()
        if last_radio_song is not None:
            # song["startDate"] is a string, e.g. 2024-01-08T20:09:10.909Z
            time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            songs = [song for song in songs if datetime.strptime(song["startDate"], time_format) > last_radio_song.start_time]
        return songs


    def query_songs(self):
        data = self.download_data()
        song_edges = data["data"]["page"]["songs"]["paginatedItems"]["edges"]
        songs_nodes = [song["node"] for song in song_edges]
        return songs_nodes

    def download_data(self):
        cookies = {}
        headers = {}

        page_id = f'/vrtnu/livestream/audio/{self.radio}.model.json'
        json_data = {
            'query': self.get_query_str(),
            'operationName': 'Livestream',
            'variables': {
                'pageId': page_id,
            },
        }

        response = requests.post('https://www.vrt.be/vrtnu-api/graphql/public/v1', cookies=cookies, headers=headers,
                                 json=json_data)

        return response.json()

    def get_query_str(self):
        # open the file "vrt.graphql", which is in the same folder as this python file
        path = os.path.join(os.path.dirname(__file__), "vrt.graphql")
        with open(path, "r") as f:
            return f.read()

    def get_last_submitted_radio_song(self):
        return Database.Util.get_last_radio_song()
