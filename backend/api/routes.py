"""
Routes API REST pour Music Book Generator
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from models.song import db, Song
from models.book import Book
from models.book_song import BookSong
from werkzeug.utils import secure_filename
import os
import json

api_bp = Blueprint('api', __name__)


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}


# ============================================
# CATALOG ENDPOINTS
# ============================================

@api_bp.route('/catalog', methods=['GET'])
def get_catalog():
    """Liste des morceaux avec filtres optionnels"""
    instrument = request.args.get('instrument')
    difficulty = request.args.get('difficulty')
    artist = request.args.get('artist')
    search = request.args.get('search')
    source = request.args.get('source')
    genre = request.args.get('genre')
    sort = request.args.get('sort', 'title_asc')

    query = Song.query

    if instrument:
        query = query.filter(Song.instruments.contains(f'"{instrument}"'))
    if difficulty:
        query = query.filter(Song.difficulty == difficulty)
    if artist:
        query = query.filter(Song.artist.ilike(f'%{artist}%'))
    if source:
        query = query.filter(Song.source == source)
    if genre:
        query = query.filter(Song.genre.ilike(f'%{genre}%'))
    if search:
        query = query.filter(
            db.or_(
                Song.title.ilike(f'%{search}%'),
                Song.artist.ilike(f'%{search}%')
            )
        )

    # Sorting
    sort_map = {
        'title_asc': Song.title.asc(),
        'title_desc': Song.title.desc(),
        'artist_asc': Song.artist.asc(),
        'artist_desc': Song.artist.desc(),
    }
    order = sort_map.get(sort, Song.title.asc())
    songs = query.order_by(order).all()
    return jsonify([song.to_dict() for song in songs])


@api_bp.route('/catalog/filters', methods=['GET'])
def get_catalog_filters():
    """Retourne les valeurs distinctes pour les filtres du catalogue"""
    sources = [r[0] for r in db.session.query(Song.source).distinct()
               if r[0] is not None and r[0].strip()]
    genres = [r[0] for r in db.session.query(Song.genre).distinct()
              if r[0] is not None and r[0].strip()]
    artists = [r[0] for r in db.session.query(Song.artist).distinct()
               if r[0] is not None and r[0].strip()]

    return jsonify({
        'sources': sorted(sources),
        'genres': sorted(genres),
        'artists': sorted(artists)
    })


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
    if 'source' in data:
        song.source = data['source']
    if 'type' in data:
        song.type = data['type']
    if 'tuning' in data:
        song.tuning = data['tuning']
    if 'youtube_url' in data:
        song.youtube_url = data['youtube_url']

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

    for field in ['title', 'instrument', 'format', 'orientation',
                   'include_toc', 'include_index', 'include_cover',
                   'include_index_title', 'include_index_artist', 'include_index_genre',
                   'page_numbers', 'page_number_position',
                   'margin_top', 'margin_bottom', 'margin_left', 'margin_right',
                   'filename_pattern']:
        if field in data:
            setattr(book, field, data[field])

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
# GENERATION ENDPOINTS
# ============================================

@api_bp.route('/books/<int:book_id>/generate', methods=['POST'])
def generate_book(book_id):
    """Générer le PDF du book"""
    book = Book.query.get_or_404(book_id)

    if not book.book_songs:
        return jsonify({'error': 'Le book ne contient aucun morceau'}), 400

    try:
        from services.pdf_generator import MusicBookGenerator
        generator = MusicBookGenerator()
        output_path = generator.generate_from_book_id(book_id)

        book.pdf_path = output_path
        db.session.commit()

        return jsonify({
            'message': 'PDF généré avec succès',
            'pdf_path': output_path,
            'book_id': book_id
        })
    except Exception as e:
        current_app.logger.error(f"Erreur génération book {book_id}: {e}")
        return jsonify({'error': f'Erreur de génération: {str(e)}'}), 500


@api_bp.route('/books/<int:book_id>/download', methods=['GET'])
def download_book(book_id):
    """Télécharger ou ouvrir le PDF d'un book"""
    book = Book.query.get_or_404(book_id)

    if not book.pdf_path or not os.path.exists(book.pdf_path):
        return jsonify({'error': 'Aucun PDF disponible pour ce book'}), 404

    as_attachment = request.args.get('dl') == '1'
    return send_file(
        book.pdf_path,
        mimetype='application/pdf',
        as_attachment=as_attachment,
        download_name=f"{book.title}.pdf"
    )


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
# IMPORT/EXPORT ENDPOINTS
# ============================================

@api_bp.route('/import/pdf', methods=['POST'])
def import_pdf():
    """Upload de PDF — réception multipart, sauvegarde et création Song"""
    from PyPDF2 import PdfReader
    from config import Config

    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    instrument = request.form.get('instrument', 'guitar')
    if instrument not in Config.PDF_STORAGE:
        return jsonify({'error': f'Invalid instrument: {instrument}'}), 400

    dest_dir = Config.PDF_STORAGE[instrument]
    os.makedirs(dest_dir, exist_ok=True)

    results = []
    files = request.files.getlist('files')

    for file in files:
        if not file or not file.filename or not allowed_file(file.filename):
            results.append({'filename': getattr(file, 'filename', '?'), 'status': 'skipped', 'reason': 'Not a PDF'})
            continue

        filename = secure_filename(file.filename)
        filepath = os.path.join(dest_dir, filename)

        # Avoid overwriting
        if os.path.exists(filepath):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filename = f"{base}_{counter}{ext}"
                filepath = os.path.join(dest_dir, filename)
                counter += 1

        file.save(filepath)

        # Count pages
        try:
            reader = PdfReader(filepath)
            pages = len(reader.pages)
        except Exception:
            pages = 1

        # Extract title from filename
        title = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()

        # Create Song in DB
        song = Song(
            title=title,
            pdf_path=filepath,
            pages=pages,
            instruments=json.dumps([instrument])
        )
        db.session.add(song)
        db.session.commit()

        results.append({
            'filename': filename,
            'status': 'imported',
            'song_id': song.id,
            'title': song.title,
            'pages': pages
        })

    return jsonify({'results': results, 'imported': sum(1 for r in results if r['status'] == 'imported')})



@api_bp.route('/export/catalog', methods=['GET'])
def export_catalog():
    """Export du catalogue en JSON téléchargeable"""
    songs = Song.query.order_by(Song.title).all()
    data = [song.to_dict() for song in songs]

    response = current_app.response_class(
        json.dumps(data, indent=2, ensure_ascii=False),
        mimetype='application/json'
    )
    response.headers['Content-Disposition'] = 'attachment; filename=catalog_export.json'
    return response
