"""
Routes API REST pour Music Book Generator
"""

from flask import Blueprint, request, jsonify
from models.song import db, Song
from models.book import Book
from models.book_song import BookSong
from werkzeug.utils import secure_filename
import os
import json

api_bp = Blueprint('api', __name__)


# ============================================
# CATALOG ENDPOINTS
# ============================================

@api_bp.route('/catalog', methods=['GET'])
def get_catalog():
    """Liste des morceaux avec filtres optionnels"""
    # Paramètres de filtrage
    instrument = request.args.get('instrument')
    difficulty = request.args.get('difficulty')
    artist = request.args.get('artist')
    search = request.args.get('search')

    # Query de base
    query = Song.query

    # Filtres
    if instrument:
        query = query.filter(Song.instruments.contains(f'"{instrument}"'))
    if difficulty:
        query = query.filter(Song.difficulty == difficulty)
    if artist:
        query = query.filter(Song.artist.ilike(f'%{artist}%'))
    if search:
        query = query.filter(
            db.or_(
                Song.title.ilike(f'%{search}%'),
                Song.artist.ilike(f'%{search}%')
            )
        )

    songs = query.order_by(Song.title).all()
    return jsonify([song.to_dict() for song in songs])


@api_bp.route('/catalog/<int:song_id>', methods=['GET'])
def get_song(song_id):
    """Détails d'un morceau"""
    song = Song.query.get_or_404(song_id)
    return jsonify(song.to_dict())


@api_bp.route('/catalog', methods=['POST'])
def create_song():
    """Ajouter un morceau au catalogue"""
    data = request.get_json()

    song = Song.from_dict(data)
    db.session.add(song)
    db.session.commit()

    return jsonify(song.to_dict()), 201


@api_bp.route('/catalog/<int:song_id>', methods=['PUT'])
def update_song(song_id):
    """Modifier les métadonnées d'un morceau"""
    song = Song.query.get_or_404(song_id)
    data = request.get_json()

    # Mise à jour des champs
    if 'title' in data:
        song.title = data['title']
    if 'artist' in data:
        song.artist = data['artist']
    if 'key' in data:
        song.key = data['key']
    if 'tempo' in data:
        song.tempo = data['tempo']
    if 'genre' in data:
        song.genre = data['genre']
    if 'difficulty' in data:
        song.difficulty = data['difficulty']
    if 'instruments' in data:
        song.instruments = json.dumps(data['instruments'])
    if 'tags' in data:
        song.tags = json.dumps(data['tags'])
    if 'notes' in data:
        song.notes = data['notes']
    if 'pages' in data:
        song.pages = data['pages']

    db.session.commit()
    return jsonify(song.to_dict())


@api_bp.route('/catalog/<int:song_id>', methods=['DELETE'])
def delete_song(song_id):
    """Supprimer un morceau du catalogue"""
    song = Song.query.get_or_404(song_id)

    # Optionnel : supprimer le fichier PDF
    # if os.path.exists(song.pdf_path):
    #     os.remove(song.pdf_path)

    db.session.delete(song)
    db.session.commit()

    return jsonify({'message': 'Song deleted successfully'}), 200


# ============================================
# BOOKS ENDPOINTS
# ============================================

@api_bp.route('/books', methods=['GET'])
def get_books():
    """Liste des books créés"""
    books = Book.query.order_by(Book.created_at.desc()).all()
    return jsonify([book.to_dict() for book in books])


@api_bp.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Détails d'un book"""
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())


@api_bp.route('/books', methods=['POST'])
def create_book():
    """Créer un nouveau book"""
    data = request.get_json()

    book = Book.from_dict(data)
    db.session.add(book)
    db.session.commit()

    return jsonify(book.to_dict()), 201


@api_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Modifier un book"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    if 'title' in data:
        book.title = data['title']
    if 'instrument' in data:
        book.instrument = data['instrument']
    if 'format' in data:
        book.format = data['format']
    if 'orientation' in data:
        book.orientation = data['orientation']
    if 'include_toc' in data:
        book.include_toc = data['include_toc']
    if 'include_index' in data:
        book.include_index = data['include_index']
    if 'include_cover' in data:
        book.include_cover = data['include_cover']

    db.session.commit()
    return jsonify(book.to_dict())


@api_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Supprimer un book"""
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()

    return jsonify({'message': 'Book deleted successfully'}), 200


# ============================================
# BOOK SONGS ENDPOINTS
# ============================================

@api_bp.route('/books/<int:book_id>/songs', methods=['GET'])
def get_book_songs(book_id):
    """Liste des morceaux d'un book (ordonnés)"""
    book = Book.query.get_or_404(book_id)
    book_songs = sorted(book.book_songs, key=lambda x: x.position)
    return jsonify([bs.to_dict() for bs in book_songs])


@api_bp.route('/books/<int:book_id>/add_song', methods=['POST'])
def add_song_to_book(book_id):
    """Ajouter un morceau à un book"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    song_id = data.get('song_id')
    song = Song.query.get_or_404(song_id)

    # Vérifier si le morceau est compatible avec l'instrument du book
    if not song.has_instrument(book.instrument):
        return jsonify({
            'error': f'Song "{song.title}" is not compatible with {book.instrument}'
        }), 400

    # Déterminer la position (à la fin)
    max_position = db.session.query(db.func.max(BookSong.position)).filter(
        BookSong.book_id == book_id
    ).scalar() or 0

    book_song = BookSong(
        book_id=book_id,
        song_id=song_id,
        position=max_position + 1
    )

    db.session.add(book_song)
    db.session.commit()

    return jsonify(book_song.to_dict()), 201


@api_bp.route('/books/<int:book_id>/remove_song/<int:song_id>', methods=['DELETE'])
def remove_song_from_book(book_id, song_id):
    """Retirer un morceau d'un book"""
    book_song = BookSong.query.filter_by(
        book_id=book_id,
        song_id=song_id
    ).first_or_404()

    db.session.delete(book_song)
    db.session.commit()

    return jsonify({'message': 'Song removed from book'}), 200


@api_bp.route('/books/<int:book_id>/reorder', methods=['POST'])
def reorder_book_songs(book_id):
    """Réorganiser les morceaux d'un book"""
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    # data = {'song_ids': [3, 1, 5, 2]}
    song_ids = data.get('song_ids', [])

    for position, song_id in enumerate(song_ids, start=1):
        book_song = BookSong.query.filter_by(
            book_id=book_id,
            song_id=song_id
        ).first()

        if book_song:
            book_song.position = position

    db.session.commit()
    return jsonify({'message': 'Book songs reordered successfully'}), 200


# ============================================
# GENERATION ENDPOINTS (À IMPLÉMENTER)
# ============================================

@api_bp.route('/books/<int:book_id>/generate', methods=['POST'])
def generate_book(book_id):
    """Générer les PDF du book (3 versions)"""
    book = Book.query.get_or_404(book_id)

    # TODO: Implémenter la génération de PDF
    # services/pdf_generator.py

    return jsonify({
        'message': 'Book generation not implemented yet',
        'book_id': book_id
    }), 501  # Not Implemented


@api_bp.route('/books/<int:book_id>/preview', methods=['GET'])
def preview_book(book_id):
    """Preview du book (table des matières)"""
    book = Book.query.get_or_404(book_id)

    songs = book.get_songs()
    total_pages = book.get_total_pages()

    # Construire la table des matières
    toc = []
    current_page = 1

    if book.include_cover:
        current_page += 1

    if book.include_toc:
        current_page += 2  # Estimation

    for song in songs:
        toc.append({
            'title': song.title,
            'artist': song.artist,
            'page': current_page,
            'pages': song.pages or 1
        })
        current_page += song.pages or 1

    return jsonify({
        'book': book.to_dict(),
        'toc': toc,
        'total_pages': total_pages
    })


# ============================================
# IMPORT/EXPORT ENDPOINTS (À IMPLÉMENTER)
# ============================================

@api_bp.route('/import/pdf', methods=['POST'])
def import_pdf():
    """Upload de PDF"""
    # TODO: Implémenter l'upload de PDF
    return jsonify({'message': 'PDF import not implemented yet'}), 501


@api_bp.route('/export/catalog', methods=['GET'])
def export_catalog():
    """Export du catalogue (CSV/JSON)"""
    # TODO: Implémenter l'export
    return jsonify({'message': 'Catalog export not implemented yet'}), 501
