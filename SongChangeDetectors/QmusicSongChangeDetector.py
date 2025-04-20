import requests
from datetime import datetime, timezone
import json

from SongChangeDetectors.HtmlSongChangeDetector import HtmlSongChangeDetector, SimpleSongPlay

class QMusicBelgiumSongChangeDetector(HtmlSongChangeDetector):
    # https://api.qmusic.be/2.0/tracks/plays?limit=300&upto=2025-04-20T13:19:54.466Z&_station_id=qmusic_be
    # api used in https://qmusic.be/playlist
    # Note that willy uses the same API (also part op dpg)
    def __init__(self, change_handler, radio_name, station_id="qmusic_be", base="api.qmusic.be", max_songs=20):
        super().__init__(change_handler, radio_name, max_songs)
        self.station_id = station_id
        self.base_url = f"https://{base}/2.0/tracks/plays"
        self.limit = max_songs


    def query_songs(self):
        now_utc = datetime.now(timezone.utc)
        upto_time_str = now_utc.isoformat(timespec='milliseconds').replace('+00:00', 'Z')
        url = f"{self.base_url}?limit={self.limit}&upto={upto_time_str}&_station_id={self.station_id}"

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            played_tracks = data.get("played_tracks", [])
            songs = []

            for track in played_tracks:
                simple_song_play = SimpleSongPlay()
                simple_song_play.title = track.get("title")
                artist_data = track.get("artist", {})
                simple_song_play.artist = artist_data.get("name")

                played_at_str = track.get("played_at")
                if played_at_str:
                    # Parse the time string, handling the timezone offset
                    time_parsed = datetime.fromisoformat(played_at_str.replace('Z', '+00:00'))
                    # Convert to the local timezone (Belgium) for consistency if needed
                    # belgium_timezone = timezone(timedelta(hours=2))
                    # simple_song_play.start_time = time_parsed.astimezone(belgium_timezone)
                    simple_song_play.start_time = time_parsed
                else:
                    raise ValueError("Played at time is missing or invalid")

                if simple_song_play.title and simple_song_play.artist and simple_song_play.start_time:
                    songs.append(simple_song_play)
                else:
                    raise ValueError(f"Incomplete song data received: {track}: {simple_song_play.title}, {simple_song_play.artist}, {simple_song_play.start_time}")

            return songs

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Qmusic API: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON response from Qmusic API: {e}")
            return []

# Example usage:
if __name__ == "__main__":
    qmusic = QMusicBelgium()
    recent_songs = qmusic.query_songs()
    if recent_songs:
        print("Recently played songs on Qmusic Belgium:")
        for song in recent_songs:
            print(f"  Title: {song.title}, Artist: {song.artist}, Played at: {song.start_time}")
    else:
        print("Could not retrieve recently played songs.")