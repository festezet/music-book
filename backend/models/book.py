"""
Modèle Book - Représente un livre de partitions
"""

from datetime import datetime
from .song import db


class Book(db.Model):
    """Modèle pour un livre de partitions"""

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    instrument = db.Column(db.String(50), nullable=False)  # 'guitar', 'bass', 'violin'
    format = db.Column(db.String(20), default='A4')
    orientation = db.Column(db.String(20), default='portrait')
    include_toc = db.Column(db.Boolean, default=True)  # Table of contents
    include_index = db.Column(db.Boolean, default=True)  # Alphabetical index
    include_cover = db.Column(db.Boolean, default=True)  # Cover page
    pdf_path = db.Column(db.String(500), nullable=True)  # Chemin vers le PDF généré
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relations
    book_songs = db.relationship('BookSong', back_populates='book', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Book {self.title} ({self.instrument})>'

    def to_dict(self):
        """Convertir en dictionnaire pour l'API"""
        return {
            'id': self.id,
            'title': self.title,
            'instrument': self.instrument,
            'format': self.format,
            'orientation': self.orientation,
            'include_toc': self.include_toc,
            'include_index': self.include_index,
            'include_cover': self.include_cover,
            'pdf_path': self.pdf_path,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'song_count': len(self.book_songs)
        }

    @staticmethod
    def from_dict(data):
        """Créer une instance depuis un dictionnaire"""
        return Book(
            title=data.get('title'),
            instrument=data.get('instrument'),
            format=data.get('format', 'A4'),
            orientation=data.get('orientation', 'portrait'),
            include_toc=data.get('include_toc', True),
            include_index=data.get('include_index', True),
            include_cover=data.get('include_cover', True)
        )

    def get_songs(self):
        """Récupérer les morceaux du livre ordonnés par position"""
        return [bs.song for bs in sorted(self.book_songs, key=lambda x: x.position)]

    def get_total_pages(self):
        """Calculer le nombre total de pages (estimé)"""
        # Page de garde (1) + TOC (2) + morceaux + Index (1)
        base_pages = 0
        if self.include_cover:
            base_pages += 1
        if self.include_toc:
            base_pages += 2  # Estimation
        if self.include_index:
            base_pages += 1

        song_pages = sum(bs.song.pages or 0 for bs in self.book_songs)
        return base_pages + song_pages
