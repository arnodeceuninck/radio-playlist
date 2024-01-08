from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

def create_session():
    # Create SQLite database file (music_database.db) and tables
    engine = create_engine('sqlite:///radio_playlist.db', echo=True)
    Base.metadata.create_all(bind=engine)

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()

    return session