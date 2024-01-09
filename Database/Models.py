from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from Database.Database import Base

class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    spotify_id = Column(String, nullable=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"

class Playlist(Base):
    __tablename__ = 'playlist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    songs = relationship('Song', secondary='playlist_song')

class Radio(Base):
    __tablename__ = 'radio'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    songs = relationship('Song', secondary='radio_song')

class RadioSong(Base):
    __tablename__ = 'radio_song'
    radio_id = Column(Integer, ForeignKey('radio.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'), primary_key=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)

class PlaylistSong(Base):
    __tablename__ = 'playlist_song'
    playlist_id = Column(Integer, ForeignKey('playlist.id'), primary_key=True)
    song_id = Column(Integer, ForeignKey('song.id'), primary_key=True)