import os
import spotipy
import spotipy.util
import logging
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from difflib import SequenceMatcher

from Database import session, Playlist

class SpotifyPlaylistBuilder:
    def __init__(self, playlist_name = None, min_songs=50, max_songs=100):
        logging.info(f"SpotifyPlaylistBuilder started for {playlist_name}")
        scope = 'playlist-modify-public'
        # set retries to 0 in an attempt to fix endless hanging problem: https://github.com/spotipy-dev/spotipy/issues/913
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,  open_browser=False), retries=3) #client_credentials_manager=SpotifyClientCredentials())

        self.playlist = None
        self.playlist_map = self.load_playlists()
        if playlist_name is not None:
            self.switch_playlist(playlist_name)

        self.min_songs = min_songs # keep the songs between min_songs and max_songs, since removing a song each time a new song is added spams the spotify api too much
        self.max_songs = max_songs

        assert self.max_songs <= 100, "Removing songs doesn't work for more than 100 songs in a playlist. (because it's the tracks limit of a playlist in spotify api and i didn't implement pagination yet)"


    def switch_playlist(self, playlist_name):
        playlist_json = self.get_or_create_playlist(playlist_name)
        self.playlist = session.query(Playlist).filter_by(spotify_id=playlist_json['id']).first()
        assert self.playlist is not None, f"SpotifyPlaylistBuilder: Playlist '{playlist_name}' not found in database. Please remove the playlist from Spotify and restart the program."
        return self
    
    def load_playlists(self):
        # Current playlists are limited, so often the playlist is not found
        # playlists = self.spotify.current_user_playlists()
        # return {playlist['name']: playlist for playlist in playlists['items']}

        # Instead, load all playlists based on the ids from the database.
        db_playlists = session.query(Playlist).all()
        playlists = {}
        for playlist in db_playlists:
            playlist_id = playlist.spotify_id
            playlist_json = self.spotify.playlist(playlist_id)
            playlists[playlist.name] = playlist_json

        return playlists
  

    def get_or_create_playlist(self, playlist_name):
        if playlist_name not in self.playlist_map:
            raise Exception(f"SpotifyPlaylistBuilder: Playlist '{playlist_name}' not found on Spotify. All playlist should already exist in Spotify. Probably a problem with the API, try again.")
            logging.info(f"SpotifyPlaylistBuilder: Playlist '{playlist_name}' not found on Spotify. Creating new playlist.")
            self.create_playlist(playlist_name)

        return self.playlist_map[playlist_name]

    def create_playlist(self, playlist_name):
        description = "The music of live radio, with the power of Spotify. The most recently played song is at the end of this playlist. I'm not affiliated with the radio station."
        # get the username from the environment variable
        username = os.environ.get('SPOTIPY_CLIENT_USERNAME') # since this doesn't work: self.spotify.me()['id']
        playlist = self.spotify.user_playlist_create(username, playlist_name, public=True, description=description)
        self.add_playlist_in_db(playlist)

        self.playlist_map[playlist_name] = playlist

        # Somehow this gives an unauthorized error
        # Add ../icon.jpg as playlist cover 
        # with open('icon.jpg', 'rb') as f:
        #     self.spotify.playlist_upload_cover_image(playlist['id'], f)

        return playlist

    def add_song(self, radio_song):
        song = radio_song.song
        track_id = self.search_for_track_id(song)
        if track_id is None:
            logging.error(f"SpotifyPlaylistBuilder: Song '{song}' not found on Spotify")
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
            logging.info("Song found in database")
            return song.spotify_id
        
        # if not found in the database, search on Spotify
        # take three songs, search the best match
        results = self.spotify.search(q=f"{song.title} {song.artist}", type='track', limit=3)
        tracks = results['tracks']['items']
        if len(tracks) == 0:
            return None
        best_match_track = self.get_best_match(tracks, song)
        track_id = best_match_track['id']
        logging.info(f"Best match: {best_match_track['name']} - {best_match_track['artists'][0]['name']}")
        self.add_track_id_to_song(song, track_id)
        return track_id
    
    def get_best_match(self, tracks, song):
        best_match = None
        highest_similarity = 0
        
        for item in tracks:
            track_name = item['name']
            track_artist = item['artists'][0]['name']
            
            title_similarity = self.get_similarity(track_name.lower(), song.title.lower())
            artist_similarity = self.get_similarity(track_artist.lower(), song.artist.lower())
            
            overall_similarity = (title_similarity + artist_similarity) / 2
            
            if overall_similarity > highest_similarity:
                highest_similarity = overall_similarity
                best_match = item

        if best_match != tracks[0]:
            matches_str = ", ".join([f"'{track['name']} - {track['artists'][0]['name']}'" for track in tracks])
            logging.info(f"SpotifyPlaylistBuilder: Best match is not the first match for '{song}'. Options were: {matches_str}")
        
        return best_match
    
    def get_similarity(self, s1, s2):
        return SequenceMatcher(None, s1, s2).ratio()

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

            # Note that only the first 100 songs are returned if the limit is higher
            playlist = self.spotify.playlist_items(playlist_id, limit=self.max_songs)
            tracks = playlist['items']

            remove_count = len(tracks) - self.min_songs
            if remove_count < 0:
                return [], []
            remove_count = min(remove_count, len(tracks))

            logging.info(f"Removing {remove_count} songs out of {self.playlist.song_count} songs from the playlist")

            return list([track['track']['id'] for track in tracks[:remove_count]]), list(range(0, remove_count))
        return [], []