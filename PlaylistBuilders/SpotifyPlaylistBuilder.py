import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyPlaylistBuilder:
    def __init__(self):
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.playlist = None # TODO

    def add_song(self, song):
        track_id = self.search_for_track_id(song)
        self.spotify.playlist_add_items(self.playlist, [track_id])
        print(f"SpotifyPlaylistBuilder: Song '{song}' added to playlist")

    def search_for_track_id(self, song):
        results = self.spotify.search(q=f"track:{song.title} artist:{song.artist}", type='track')
        track_id = results['tracks']['items'][0]['id']
        return track_id