import os
import requests

from Models.Song import Song
from SongChangeDetectors.SongChangeDetector import SongChangeDetector

class VRTSongChangeDetector(SongChangeDetector):
    def __init__(self, radio="mnmhits"):
        super().__init__()

        assert radio in ["mnmhits", "mnm", "stubru"], "Radio not supported"
        self.radio = radio

    def start(self):
        print("SongChangeDetector started")
        songs = self.query_songs()
        last_song = self.get_last_submitted_song()
        if last_song is not None:
            songs = [song for song in songs if song.time > last_song.time]
        self.change_handler(new_songs=songs)

    def query_songs(self):
        data = self.download_data()
        song_edges = data["data"]["page"]["songs"]["paginatedItems"]["edges"]
        songs_nodes = [song["node"] for song in song_edges]
        songs = [Song(title=song["title"], artist=song["description"], time=song["startDate"]) for song in songs_nodes]
        return songs

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

    def get_last_submitted_song(self):
        return None