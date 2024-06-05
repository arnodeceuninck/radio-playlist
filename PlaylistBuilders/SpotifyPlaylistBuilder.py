import os
import spotipy
import spotipy.util
import logging
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

from Database import session, Playlist


class SpotifyPlaylistBuilder:
    def __init__(self, playlist_name, min_songs=80, max_songs=120):
        logging.info(f"SpotifyPlaylistBuilder started for {playlist_name}")
        scope = 'playlist-modify-public'
        # set retries to 0 in an attempt to fix endless hanging problem: https://github.com/spotipy-dev/spotipy/issues/913
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,  open_browser=False), retries=0) #client_credentials_manager=SpotifyClientCredentials())

        playlist_json = self.get_or_create_playlist(playlist_name)
        self.playlist = session.query(Playlist).filter_by(spotify_id=playlist_json['id']).first()

        self.min_songs = min_songs # keep the songs between min_songs and max_songs, since removing a song each time a new song is added spams the spotify api too much
        self.max_songs = max_songs

        assert self.playlist is not None, f"SpotifyPlaylistBuilder: Playlist '{playlist_name}' not found in database. Please remove the playlist from Spotify and restart the program."


    def get_or_create_playlist(self, playlist_name):
        playlists = self.spotify.current_user_playlists()
        for playlist in playlists['items']:
            if playlist['name'] == playlist_name:
                logging.info(f"SpotifyPlaylistBuilder: Playlist '{playlist_name}' found on Spotify with id {playlist['id']}.")
                return playlist
        logging.info(f"SpotifyPlaylistBuilder: Playlist '{playlist_name}' not found on Spotify. Creating new playlist.")
        return self.create_playlist(playlist_name)

    def create_playlist(self, playlist_name):
        description = "The music of live radio, with the power of Spotify. The most recently played song is at the end of this playlist. I'm not affiliated with the radio station."
        # get the username from the environment variable
        username = os.environ.get('SPOTIPY_CLIENT_USERNAME') # since this doesn't work: self.spotify.me()['id']
        playlist = self.spotify.user_playlist_create(username, playlist_name, public=True, description=description)
        self.add_playlist_in_db(playlist)

        # Somehow this gives an unauthorized error
        # Add ../icon.jpg as playlist cover 
        # with open('icon.jpg', 'rb') as f:
        #     self.spotify.playlist_upload_cover_image(playlist['id'], f)

        return playlist

    def add_song(self, radio_song):
        song = radio_song.song
        track_id = self.search_for_track_id(song)
        if track_id is None:
            logging(f"SpotifyPlaylistBuilder: Song '{song}' not found on Spotify")
            return
        logging.info(f"SpotifyPlaylistBuilder: Song '{song}' found on Spotify with id {track_id}")
        track_str = f"spotify:track:{track_id}"

        
        self.spotify.playlist_add_items(self.playlist.spotify_str(), [track_str])
        logging.info(f"SpotifyPlaylistBuilder: Song '{song}' added to playlist")

        self.playlist.song_count += 1

        self.remove_oldest_songs_if_needed()


    def search_for_track_id(self, song):
        # first search in the database
        if song.spotify_id is not None:
            return song.spotify_id
        
        # if not found in the database, search on Spotify
        results = self.spotify.search(q=f"{song.title} {song.artist}", type='track', limit=1)
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
        playlist = Playlist(name=playlist_name, spotify_id=playlist_id, song_count=0)
        session.add(playlist)
        session.commit()

    def remove_oldest_songs_if_needed(self):
        songs, positions = self.get_song_ids_to_remove()

        if len(songs) == 0:
            return
        
        logging.info(f"SpotifyPlaylistBuilder: Removing oldest songs from playlist")
        # self.spotify.playlist_remove_specific_occurrences_of_items(self.playlist.spotify_str(),
        #                                                            [{ "uri": songs, "positions":positions }])
        remove_list = list([{"uri": song, "positions": position} for song, position in zip(songs, positions)])
        self.spotify.playlist_remove_specific_occurrences_of_items(self.playlist.spotify_str(), remove_list)
        
        self.playlist.song_count = self.min_songs
        session.commit()

    def get_song_ids_to_remove(self):
        if self.playlist.song_count > self.max_songs:
            playlist_id = self.playlist.spotify_id
            # playlist = self.spotify.playlist(playlist_id)
            # tracks = playlist['tracks']['items']
            playlist = self.spotify.playlist_items(playlist_id, limit=self.max_songs+1)
            tracks = playlist['items']

            remove_count = self.playlist.song_count - self.min_songs
            remove_count = min(remove_count, len(tracks))

            return list([track['track']['id'] for track in tracks[:remove_count]]), list(range(0, remove_count))
        return [], []