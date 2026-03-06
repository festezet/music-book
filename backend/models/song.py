"""
Modèle Song - Représente un morceau de musique dans le catalogue
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


class Song(db.Model):
    """Modèle pour un morceau de musique"""

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    artist = db.Column(db.String(255))
    key = db.Column(db.String(10))  # Tonalité (C, Dm, G7, etc.)
    tempo = db.Column(db.Integer)   # BPM
    genre = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))  # 'easy', 'medium', 'advanced'
    instruments = db.Column(db.Text)  # JSON array: ["guitar", "bass"]
    tags = db.Column(db.Text)  # JSON array: ["acoustic", "fingerstyle"]
    pdf_path = db.Column(db.String(500), nullable=False)
    pages = db.Column(db.Integer)
    source = db.Column(db.String(50))  # 'ultimate_guitar', 'songsterr', 'boite_chansons'
    type = db.Column(db.String(20))    # 'chords', 'tab'
    youtube_url = db.Column(db.String(255))  # Lien YouTube vers la chanson
    tuning = db.Column(db.String(50))  # Accordage (E A D G B E, Drop D, etc.)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    book_songs = db.relationship('BookSong', back_populates='song', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Song {self.title} by {self.artist}>'

    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'title': self.title,
            'artist': self.artist,
            'key': self.key,
            'tempo': self.tempo,
            'genre': self.genre,
            'difficulty': self.difficulty,
            'instruments': json.loads(self.instruments) if self.instruments else [],
            'tags': json.loads(self.tags) if self.tags else [],
            'pdf_path': self.pdf_path,
            'pages': self.pages,
            'source': self.source,
            'type': self.type,
            'youtube_url': self.youtube_url,
            'tuning': self.tuning,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @staticmethod
    def from_dict(data):
        """Créer une instance depuis un dictionnaire"""
        instruments = data.get('instruments', [])
        tags = data.get('tags', [])

        return Song(
            title=data.get('title'),
            artist=data.get('artist'),
            key=data.get('key'),
            tempo=data.get('tempo'),
            genre=data.get('genre'),
            difficulty=data.get('difficulty'),
            instruments=json.dumps(instruments) if instruments else None,
            tags=json.dumps(tags) if tags else None,
            pdf_path=data.get('pdf_path'),
            pages=data.get('pages'),
            source=data.get('source'),
            type=data.get('type'),
            notes=data.get('notes')
        )

    def has_instrument(self, instrument):
        """Vérifier si le morceau est compatible avec un instrument"""
        if not self.instruments:
            return False
        instruments_list = json.loads(self.instruments)
        return instrument in instruments_list
