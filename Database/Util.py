from Database import Song, RadioSong, session, Radio
from sqlalchemy import desc, column

def get_last_radio_song(radio_name):
    return session.query(RadioSong).join(Radio).filter(Radio.name == radio_name).order_by(desc(RadioSong.start_time)).first()

def get_or_create_song(title, artist):
    song = session.query(Song).filter_by(title=title, artist=artist).first()
    if song is None:
        song = Song(title=title, artist=artist)
        session.add(song)
        session.commit()
    return song

def get_or_create_radio(name):
    radio = session.query(Radio).filter_by(name=name).first()
    if radio is None:
        radio = Radio(name=name)
        session.add(radio)
        session.commit()
    return radio