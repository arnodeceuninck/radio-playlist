from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os

Base = declarative_base()

def create_session():
    # Get the required information from the .env file
    db_host = 'postgres'
    db_port = '5432'
    db_name = os.getenv('POSTGRES_DB')
    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')

    # Create the connection string
    db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

    # Create the engine and connect to the database
    engine = create_engine(db_url, echo=True)
    Base.metadata.create_all(bind=engine)

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()

    return session

# def create_session():
#     # Create SQLite database file (music_database.db) and tables
#     engine = create_engine('sqlite:///radio_playlist.db', echo=True)
#     Base.metadata.create_all(bind=engine)

#     # Create a session to interact with the database
#     Session = sessionmaker(bind=engine)
#     session = Session()

#     return session