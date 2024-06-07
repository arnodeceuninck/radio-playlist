import os
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import spotipy.util
import dotenv

dotenv.load_dotenv()

scope = 'playlist-modify-public'
client_username = os.environ.get('SPOTIPY_CLIENT_USERNAME')


dotenv.load_dotenv(custom_env)

cache_file = f'.cache-{client_username}'

if os.path.exists(cache_file):
    exit(0)

auth = SpotifyOAuth(scope=scope,  open_browser=True)
sp = spotipy.Spotify(auth_manager=auth, retries=0)
# sample query to trigger authentication
_ = sp.current_user_playlists()

