from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os
import logging

Base = declarative_base()

def create_session():
    # Get the required information from the .env file
    db_url = os.getenv('DATABASE_URL')
    # db_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'


    # Create the engine and connect to the database
    engine = create_engine(db_url)
    Base.metadata.create_all(bind=engine)

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    session = Session()

    return session
