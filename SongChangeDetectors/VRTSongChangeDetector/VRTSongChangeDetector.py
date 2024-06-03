import os
import time
import requests
import util
from datetime import datetime

import Database.Util
from Database import Song, session, RadioSong
from SongChangeDetectors.SongChangeDetector import SongChangeDetector

radios = {
    "mnm": "MNM",
    "mnmhits": "MNM Hits",
    "stubru": "Studio Brussel (StuBru)"
}

class VRTSongChangeDetector(SongChangeDetector):
    def __init__(self, radio, change_handler):
        super().__init__(change_handler)
        assert radio in radios, f"radio must be one of {radios.keys()}"
        self.radio = radio
        self.radio_name = radios[self.radio]

    def start(self):
        print("SongChangeDetector started")
        while True:
            self.handle_new_songs()
            time.sleep(60)


    def handle_new_songs(self):
        new_songs = self.query_songs()
        new_songs = self.filter_new_songs(new_songs)
        new_songs = sorted(new_songs, key=lambda song: datetime.strptime(song['startDate'], '%Y-%m-%dT%H:%M:%S.%fZ'))
        for new_song in new_songs:
            print(f"New song: {new_song['title']} - {new_song['description']}")
            radio_song = self.create_db_radio_song(new_song)
            self.change_handler(radio_song)
            # raise Exception("Stop here for debugging purposes")

    def create_db_radio_song(self, song):
        title = song["title"]
        artist = song["description"]
        start = util.str_to_time(song["startDate"])
        end = util.str_to_time(song["endDate"])

        song = Database.Util.get_or_create_song(title, artist)
        radio = Database.Util.get_or_create_radio(name=self.radio_name)
        radio_song = RadioSong(radio_id=radio.id, song_id=song.id, start_time=start, end_time=end)

        session.add(radio_song)
        session.commit()

        return radio_song

    def filter_new_songs(self, songs):
        last_radio_song = self.get_last_submitted_radio_song()
        if last_radio_song is not None:
            songs = [song for song in songs if util.str_to_time(song["startDate"]) > last_radio_song.start_time]
        return songs


    def query_songs(self):
        data = self.download_data()
        song_edges = data["data"]["component"]["components"][0]["paginatedItems"]["edges"]
        songs_nodes = [song["node"] for song in song_edges]
        return songs_nodes

    def download_data(self):
        cookies = {}
        headers = {
            'x-vrt-client-name': 'WEB',
        }

        # page_id = f'/vrtnu/livestream/audio/{self.radio}.model.json'
        json_data = {
            'query': self.get_query_str(),
            # 'operationName': 'Livestream',
            'operationName': 'component',
            'variables': {
                # 'pageId': page_id,
                'componentId': '#Y25pLWFsc3BnfHBsYXlsaXN0I21ubWhpdHM='
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
        return Database.Util.get_last_radio_song(self.radio_name)
