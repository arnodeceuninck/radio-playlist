import os
from pathlib import Path

def load_cache_from_env():
    """Load cache file from environment variable if it exists."""
    cache_content = os.getenv('SPOTIFY_CACHE')
    username = os.getenv('SPOTIPY_CLIENT_USERNAME')
    
    if cache_content and username:
        cache_file = Path(f'.cache-{username}')
        cache_file.write_text(cache_content)
        print(f"Cache loaded from environment variable for user {username}")
        return True
    
    return False
