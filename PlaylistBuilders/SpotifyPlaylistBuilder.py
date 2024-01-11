import os
import spotipy
import spotipy.util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from Database import session, Playlist


class SpotifyPlaylistBuilder:
    def __init__(self, playlist_name):
        scope = 'playlist-modify-public'
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope)) #client_credentials_manager=SpotifyClientCredentials())

        playlist_json = self.get_or_create_playlist(playlist_name)
        self.playlist = session.query(Playlist).filter_by(spotify_id=playlist_json['id']).first()
        assert self.playlist is not None, f"SpotifyPlaylistBuilder: Playlist '{playlist_name}' not found in database. Please remove the playlist from Spotify and restart the program."


    def get_or_create_playlist(self, playlist_name):
        playlists = self.spotify.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                return playlist
        return self.create_playlist(playlist_name)

    def create_playlist(self, playlist_name):
        description = "The music of live radio, with the power of Spotify. The most recently played song is at the end of this playlist. I'm not affiliated with the radio station."
        # get the username from the environment variable
        username = os.environ.get('SPOTIPY_CLIENT_USERNAME') # since this doesn't work: self.spotify.me()['id']
        playlist = self.spotify.user_playlist_create(username, playlist_name, public=True, description=description)
        self.add_playlist_in_db(playlist)
        return playlist

    def add_song(self, radio_song):
        song = radio_song.song
        track_id = self.search_for_track_id(song)
        if track_id is None:
            print(f"SpotifyPlaylistBuilder: Song '{song}' not found on Spotify")
            return
        track_str = f"spotify:track:{track_id}"
        self.spotify.playlist_add_items(self.playlist.spotify_str(), [track_str])

        self.remove_oldest_song_if_needed()

        print(f"SpotifyPlaylistBuilder: Song '{song}' added to playlist")

    def search_for_track_id(self, song):
        results = self.spotify.search(q=f"track:{song.title} artist:{song.artist}", type='track', limit=1)
        tracks = results['tracks']['items']
        if len(tracks) == 0:
            return None
        track_id = tracks[0]['id']
        self.add_track_id_to_song(song, track_id)
        return track_id

    def add_track_id_to_song(self, song, track_id):
        song.spotify_id = track_id
        session.commit()

    def add_playlist_in_db(self, playlist):
        playlist_id = playlist['id']
        playlist_name = playlist['name']
        playlist = Playlist(name=playlist_name, spotify_id=playlist_id)
        session.add(playlist)
        session.commit()

    def remove_oldest_song_if_needed(self):
        song = self.get_song_id_to_remove()

        if song is None:
            return

        self.spotify.playlist_remove_specific_occurrences_of_items(self.playlist.spotify_str(),
                                                                   [{ "uri": song, "positions":[0] }])
        self.remove_song_in_db(song)

    def get_song_id_to_remove(self):
        # get the first song in the playlist using the spotify api
        playlist_id = self.playlist.spotify_id
        playlist = self.spotify.playlist(playlist_id)
        tracks = playlist['tracks']['items']

        if len(tracks) < 101:
            return None

        track = tracks[0]
        track_id = track['track']['id']
        return track_id