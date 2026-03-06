"""
Modèle BookSong - Table d'association entre Book et Song
"""

from .song import db


class BookSong(db.Model):
    """Table d'association entre Book et Song avec ordre"""

    __tablename__ = 'book_songs'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)  # Ordre dans le book

    # Relations
    book = db.relationship('Book', back_populates='book_songs')
    song = db.relationship('Song', back_populates='book_songs')

    def __repr__(self):
        return f'<BookSong book_id={self.book_id} song_id={self.song_id} position={self.position}>'

    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'song_id': self.song_id,
            'position': self.position,
            'song': self.song.to_dict() if self.song else None
        }
