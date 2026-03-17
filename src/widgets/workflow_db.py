"""
Workflow DB helpers - Database operations for the workflow GUI.
Extracted from workflow_gui.py for modularity.
"""
import sys
import os
from typing import Optional, List


def _get_backend_path():
    """Get the backend path for imports."""
    return os.path.join(os.path.dirname(__file__), '..', '..', 'backend')


def load_book_songs(book_id: int) -> List[int]:
    """Charge les song_ids d'un book depuis la BDD"""
    sys.path.insert(0, _get_backend_path())

    try:
        from app import app, db
        from models.book_song import BookSong

        with app.app_context():
            book_songs = BookSong.query.filter_by(book_id=book_id)\
                .order_by(BookSong.position).all()
            return [bs.song_id for bs in book_songs]
    except Exception as e:
        print(f"Erreur chargement morceaux du book: {e}")
        return []


def save_book_songs(book_id: int, song_ids: List[int]) -> bool:
    """Sauvegarde les morceaux d'un book dans la BDD"""
    sys.path.insert(0, _get_backend_path())

    try:
        from app import app, db
        from models.book_song import BookSong

        with app.app_context():
            # Supprimer les anciennes associations
            BookSong.query.filter_by(book_id=book_id).delete()

            # Ajouter les nouvelles
            for position, song_id in enumerate(song_ids, 1):
                book_song = BookSong(
                    book_id=book_id,
                    song_id=song_id,
                    position=position
                )
                db.session.add(book_song)

            db.session.commit()
            print(f"Book {book_id} sauvegarde: {len(song_ids)} morceaux")
            return True
    except Exception as e:
        print(f"Erreur sauvegarde morceaux: {e}")
        return False


def generate_default_book_name() -> str:
    """Generate a default book name like 'Mon Music Book 1', 'Mon Music Book 2', etc."""
    sys.path.insert(0, _get_backend_path())

    try:
        from app import app, db
        from models.book import Book

        with app.app_context():
            existing = Book.query.filter(Book.title.like("Mon Music Book%")).all()
            numbers = []
            for book in existing:
                title = book.title
                if title == "Mon Music Book":
                    numbers.append(1)
                elif title.startswith("Mon Music Book "):
                    try:
                        num = int(title.replace("Mon Music Book ", ""))
                        numbers.append(num)
                    except ValueError:
                        pass

            next_num = max(numbers, default=0) + 1
            if next_num == 1:
                return "Mon Music Book"
            return f"Mon Music Book {next_num}"
    except Exception as e:
        print(f"Erreur generation nom: {e}")
        return "Mon Music Book"


def create_book_in_db(title: str) -> Optional[int]:
    """Create a new book in the database and return its ID"""
    sys.path.insert(0, _get_backend_path())

    try:
        from app import app, db
        from models.book import Book

        with app.app_context():
            book = Book(
                title=title,
                instrument='guitar',
                include_cover=True,
                include_toc=True,
                include_index=True
            )
            db.session.add(book)
            db.session.commit()
            print(f"Nouveau book cree: {title} (ID: {book.id})")
            return book.id
    except Exception as e:
        print(f"Erreur creation book: {e}")
        return None


def update_book_title_in_db(book_id: int, new_title: str) -> bool:
    """Update book title in database"""
    sys.path.insert(0, _get_backend_path())

    try:
        from app import app, db
        from models.book import Book

        with app.app_context():
            book = Book.query.get(book_id)
            if book:
                book.title = new_title
                db.session.commit()
                return True
            return False
    except Exception as e:
        print(f"Erreur mise a jour titre: {e}")
        return False
