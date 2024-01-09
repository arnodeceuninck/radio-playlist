import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyPlaylistBuilder:
    def __init__(self, playlist_name):
        # TODO: use another way to authenticate: https://github.com/spotipy-dev/spotipy/issues/240
        self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        self.playlist = self.get_or_create_playlist(playlist_name)


    def get_or_create_playlist(self, playlist_name):
        playlists = self.spotify.user_playlists('spotify') # TODO? current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                return playlist
        return self.create_playlist(playlist_name)

    def create_playlist(self, playlist_name):
        description = "The music of live radio, with the power of Spotify. I'm not affiliated with the radio station."
        # get the username from the environment variable
        username = os.environ.get('SPOTIPY_CLIENT_USERNAME') # since this doesn't work: self.spotify.me()['id']
        playlist = self.spotify.user_playlist_create(username, playlist_name, public=True, description=description)
        return playlist

    def add_song(self, radio_song):
        song = radio_song.song
        track_id = self.search_for_track_id(song)
        self.spotify.playlist_add_items(self.playlist, [track_id])
        print(f"SpotifyPlaylistBuilder: Song '{song}' added to playlist")

    def search_for_track_id(self, song):
        results = self.spotify.search(q=f"track:{song.title} artist:{song.artist}", type='track', limit=1)
        track_id = results['tracks']['items'][0]['id']
        return track_id