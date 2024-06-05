from Database.Models import Song, Playlist, Radio, RadioSong
from Database.Database import create_postgres_session, create_sqlite_session

# session = create_postgres_session()

session = create_sqlite_session()