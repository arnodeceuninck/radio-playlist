from Database.Models import Song, Playlist, Radio, RadioSong
from Database.Database import create_session
from dotenv import load_dotenv

load_dotenv()

session = create_session()