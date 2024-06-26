from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from Database.Database import Base

class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    spotify_id = Column(String, nullable=True)

    radios = relationship('RadioSong', back_populates='song')

    def __str__(self):
        return f"{self.title} - {self.artist}"

class Playlist(Base):
    __tablename__ = 'playlist'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    spotify_id = Column(String, nullable=True)
    song_count = Column(Integer, nullable=False, default=0) # have an estimation of the number of songs in the playlist, to prevent spamming the spotify api

    def __str__(self):
        return self.name

    def spotify_str(self):
        return f"spotify:playlist:{self.spotify_id}"

    def length(self):
        return len(self.songs)

class Radio(Base):
    __tablename__ = 'radio'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    songs = relationship('RadioSong', back_populates='radio')

class RadioSong(Base):
    __tablename__ = 'radio_song'

    id = Column(Integer, primary_key=True, autoincrement=True)

    radio_id = Column(Integer, ForeignKey('radio.id'))
    song_id = Column(Integer, ForeignKey('song.id'))
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)

    song = relationship('Song', back_populates='radios')
    radio = relationship('Radio', back_populates='songs')

