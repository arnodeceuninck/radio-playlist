from sqlalchemy import func
from sqlalchemy.orm import aliased

from Database import session, RadioSong, Radio, Song

radio_name = 'MNM Hits'

# Query to get the top 10 most played songs and total number of songs for a specific radio
query = (
    session.query(
        Song,
        func.count().label('play_count'),
        func.count().over().label('total_songs')
    )
    .join(RadioSong, Song.id == RadioSong.song_id)
    .join(Radio, Radio.id == RadioSong.radio_id)
    .filter(Radio.name == radio_name)
    .group_by(Song.id)
    .order_by(func.count().desc())
    .limit(10)
)

# Execute the query and print the results
results = query.all()

# Print the top 10 most played songs and the total number of songs
print(f"Top 10 most played songs for radio '{radio_name}':")
for index, (song, play_count, total_songs) in enumerate(results, start=1):
    print(f"{index}. {song.title} - {song.artist} (Play Count: {play_count})")

# Print the total number of songs played by the radio
if results:
    total_songs = results[0].total_songs
    print(f"Total number of songs played by {radio_name}: {total_songs}")
else:
    print(f"No songs found for radio '{radio_name}'.")
