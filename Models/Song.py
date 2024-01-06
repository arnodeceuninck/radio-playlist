class Song:
    def __init__(self, title, artist, time=None):
        assert isinstance(title, str), "title should be a string"
        assert isinstance(artist, str), "artist should be a string"
        assert title is not None, "title should not be None"

        self.title = title
        self.artist = artist
        self.time = time # Time the song is played, can be used e.g. for sorting the songs

    def __str__(self):
        return f"{self.title} - {self.artist}"