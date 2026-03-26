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
    # Index options
    include_index_title = db.Column(db.Boolean, default=True)
    include_index_artist = db.Column(db.Boolean, default=False)
    include_index_genre = db.Column(db.Boolean, default=False)
    # Page numbering
    page_numbers = db.Column(db.Boolean, default=True)
    page_number_position = db.Column(db.String(10), default='center')  # left, center, right
    # Margins (mm)
    margin_top = db.Column(db.Integer, default=20)
    margin_bottom = db.Column(db.Integer, default=20)
    margin_left = db.Column(db.Integer, default=15)
    margin_right = db.Column(db.Integer, default=15)
    # Output
    filename_pattern = db.Column(db.String(255), default='{title}_{instrument}_{date}')
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
            'include_index_title': self.include_index_title if self.include_index_title is not None else True,
            'include_index_artist': self.include_index_artist if self.include_index_artist is not None else False,
            'include_index_genre': self.include_index_genre if self.include_index_genre is not None else False,
            'page_numbers': self.page_numbers if self.page_numbers is not None else True,
            'page_number_position': self.page_number_position or 'center',
            'margin_top': self.margin_top if self.margin_top is not None else 20,
            'margin_bottom': self.margin_bottom if self.margin_bottom is not None else 20,
            'margin_left': self.margin_left if self.margin_left is not None else 15,
            'margin_right': self.margin_right if self.margin_right is not None else 15,
            'filename_pattern': self.filename_pattern or '{title}_{instrument}_{date}',
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
            include_cover=data.get('include_cover', True),
            include_index_title=data.get('include_index_title', True),
            include_index_artist=data.get('include_index_artist', False),
            include_index_genre=data.get('include_index_genre', False),
            page_numbers=data.get('page_numbers', True),
            page_number_position=data.get('page_number_position', 'center'),
            margin_top=data.get('margin_top', 20),
            margin_bottom=data.get('margin_bottom', 20),
            margin_left=data.get('margin_left', 15),
            margin_right=data.get('margin_right', 15),
            filename_pattern=data.get('filename_pattern', '{title}_{instrument}_{date}')
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
