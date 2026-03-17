"""
Music Book Operations - Business logic extracted from music_book_gui.py.
Database queries, CRUD operations, and PDF generation.
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db
from models.song import Song
from models.book import Book
from models.book_song import BookSong


def init_database():
    """Initialize the database tables."""
    with app.app_context():
        db.create_all()


def query_catalog_songs(search='', instrument='', difficulty=''):
    """Query songs with filters. Returns list of dicts."""
    with app.app_context():
        query = Song.query
        if search:
            query = query.filter(
                db.or_(
                    Song.title.ilike(f'%{search}%'),
                    Song.artist.ilike(f'%{search}%')
                )
            )
        if instrument:
            query = query.filter(Song.instruments.contains(f'"{instrument}"'))
        if difficulty:
            query = query.filter(Song.difficulty == difficulty)
        songs = query.order_by(Song.title).all()
        return [
            {
                'id': s.id, 'title': s.title, 'artist': s.artist or '',
                'instruments': ', '.join(json.loads(s.instruments) if s.instruments else []),
                'difficulty': s.difficulty or '', 'key': s.key or '',
                'pages': s.pages or ''
            }
            for s in songs
        ]


def get_song_for_edit(song_id):
    """Get song data dict for editing. Returns dict or None."""
    with app.app_context():
        song = Song.query.get(song_id)
        return song.to_dict() if song else None


def update_song_from_dict(song_id, data):
    """Update a song from dialog result data."""
    with app.app_context():
        song = Song.query.get(song_id)
        song.title = data['title']
        song.artist = data.get('artist')
        song.key = data.get('key')
        song.tempo = data.get('tempo')
        song.genre = data.get('genre')
        song.difficulty = data.get('difficulty')
        song.instruments = json.dumps(data.get('instruments', []))
        song.pages = data.get('pages')
        song.notes = data.get('notes')
        db.session.commit()


def create_song(data):
    """Create a new song from dialog result data."""
    with app.app_context():
        song = Song.from_dict(data)
        db.session.add(song)
        db.session.commit()


def delete_song_by_id(song_id):
    """Delete a song by ID."""
    with app.app_context():
        song = Song.query.get(song_id)
        if song:
            db.session.delete(song)
            db.session.commit()


def get_available_songs():
    """Get all songs ordered by title. Returns list of (id, title, artist)."""
    with app.app_context():
        songs = Song.query.order_by(Song.title).all()
        return [(s.id, s.title, s.artist or '') for s in songs]


def get_song_info(song_id):
    """Get basic song info. Returns (title, artist, pages) or None."""
    with app.app_context():
        song = Song.query.get(song_id)
        if song:
            return (song.title, song.artist or '', song.pages or '')
        return None


def calculate_book_pages(selected_songs, include_cover, include_toc, include_index):
    """Calculate total pages for book. Returns (song_count, total_pages)."""
    total_pages = 0
    with app.app_context():
        for song_id in selected_songs:
            song = Song.query.get(song_id)
            if song and song.pages:
                total_pages += song.pages
    if include_cover:
        total_pages += 1
    if include_toc:
        total_pages += 2
    if include_index:
        total_pages += 1
    return len(selected_songs), total_pages


def save_book_to_db(title, instrument, options, selected_songs):
    """Save a book to the database. Returns book ID.

    Args:
        options: dict with keys include_cover, include_toc, include_index.
    """
    with app.app_context():
        book = Book(
            title=title, instrument=instrument,
            include_cover=options.get('include_cover', False),
            include_toc=options.get('include_toc', False),
            include_index=options.get('include_index', False)
        )
        db.session.add(book)
        db.session.flush()
        for position, song_id in enumerate(selected_songs, start=1):
            db.session.add(BookSong(book_id=book.id, song_id=song_id, position=position))
        db.session.commit()
        return book.id


def generate_pdf(song_ids, title, instrument, options):
    """Generate PDF book. Returns output path.

    Args:
        options: dict with keys include_cover, include_toc, include_index.
    """
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'services'))
    from pdf_generator import MusicBookGenerator
    generator = MusicBookGenerator()
    return generator.generate_from_song_ids(
        song_ids=song_ids, title=title, instrument=instrument,
        include_cover=options.get('include_cover', False),
        include_toc=options.get('include_toc', False),
        include_index=options.get('include_index', False)
    )
