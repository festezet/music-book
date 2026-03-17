"""
Operations base de donnees pour les morceaux.

Module extrait de song_manager.py pour separer la logique DB
de la logique d'interface graphique.
"""
import os
import sys
import json
from typing import List, Dict, Any, Optional


def _ensure_backend_path():
    """Ajouter le repertoire backend au sys.path si necessaire."""
    backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
    backend_path = os.path.normpath(backend_path)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


def load_all_songs() -> List[Dict[str, Any]]:
    """Charger tous les morceaux depuis la base, tries par titre."""
    _ensure_backend_path()
    from app import app, db
    from models.song import Song

    with app.app_context():
        songs = Song.query.order_by(Song.title).all()
        return [s.to_dict() for s in songs]


def save_song(song_data: Dict[str, Any], song_id: Optional[int] = None) -> str:
    """Creer ou mettre a jour un morceau.

    Args:
        song_data: dict avec title, artist, genre, source, type,
                   instruments (list), pdf_path, pages, key, notes
        song_id: si fourni, mise a jour du morceau existant

    Returns:
        Message de succes
    """
    _ensure_backend_path()
    from app import app, db
    from models.song import Song

    instruments_json = (
        json.dumps(song_data['instruments'])
        if song_data.get('instruments') else None
    )

    with app.app_context():
        if song_id:
            song = Song.query.get(song_id)
            if song:
                song.title = song_data['title']
                song.artist = song_data.get('artist')
                song.genre = song_data.get('genre')
                song.source = song_data.get('source')
                song.type = song_data.get('type')
                song.instruments = instruments_json
                song.pdf_path = song_data['pdf_path']
                song.pages = song_data.get('pages', 1)
                song.key = song_data.get('key')
                song.notes = song_data.get('notes')
                db.session.commit()
                return f"Morceau '{song_data['title']}' mis a jour"
        else:
            song = Song(
                title=song_data['title'],
                artist=song_data.get('artist'),
                genre=song_data.get('genre'),
                source=song_data.get('source'),
                type=song_data.get('type'),
                instruments=instruments_json,
                pdf_path=song_data['pdf_path'],
                pages=song_data.get('pages', 1),
                key=song_data.get('key'),
                notes=song_data.get('notes'),
            )
            db.session.add(song)
            db.session.commit()
            return f"Morceau '{song_data['title']}' ajoute"


def delete_song(song_id: int) -> bool:
    """Supprimer un morceau par son ID. Retourne True si supprime."""
    _ensure_backend_path()
    from app import app, db
    from models.song import Song

    with app.app_context():
        song = Song.query.get(song_id)
        if song:
            db.session.delete(song)
            db.session.commit()
            return True
    return False


def import_pdf_files(filepaths: List[str]) -> Dict[str, Any]:
    """Importer plusieurs fichiers PDF en base.

    Returns:
        dict avec 'imported' (int) et 'errors' (list of str)
    """
    _ensure_backend_path()
    from app import app, db
    from models.song import Song

    imported = 0
    errors = []

    with app.app_context():
        for filepath in filepaths:
            try:
                song = _create_song_from_pdf(filepath, Song)
                db.session.add(song)
                imported += 1
            except Exception as e:
                errors.append(f"{os.path.basename(filepath)}: {e}")
        db.session.commit()

    return {'imported': imported, 'errors': errors}


def _create_song_from_pdf(filepath: str, song_cls):
    """Creer un objet Song a partir d'un fichier PDF."""
    filename = os.path.basename(filepath)
    title = os.path.splitext(filename)[0]
    pages = _count_pdf_pages(filepath)
    source = _detect_source(filename)
    song_type = _detect_type(filename)
    instruments = _detect_instruments(filename)

    return song_cls(
        title=title,
        pdf_path=filepath,
        pages=pages,
        source=source,
        type=song_type,
        instruments=json.dumps(instruments) if instruments else None,
    )


def _count_pdf_pages(filepath: str) -> int:
    """Compter les pages d'un PDF."""
    try:
        from PyPDF2 import PdfReader
        return len(PdfReader(filepath).pages)
    except Exception:
        return 1


def _detect_source(filename: str) -> Optional[str]:
    """Detecter la source depuis le nom de fichier."""
    if "Ultimate Guitar" in filename or "tabs @" in filename:
        return "ultimate_guitar"
    if "Songsterr" in filename:
        return "songsterr"
    if "Boite a chansons" in filename or "Boite a chansons" in filename:
        return "boite_chansons"
    return None


def _detect_type(filename: str) -> Optional[str]:
    """Detecter le type (tab/chords) depuis le nom de fichier."""
    lower = filename.lower()
    if "tab" in lower:
        return "tab"
    if "chord" in lower:
        return "chords"
    return None


def _detect_instruments(filename: str) -> List[str]:
    """Detecter les instruments depuis le nom de fichier."""
    lower = filename.lower()
    if "_bass" in lower or "Bass Tab" in filename:
        return ["bass"]
    if "_guitare" in lower or "Guitar" in filename:
        return ["guitar"]
    return ["guitar"]  # Par defaut
