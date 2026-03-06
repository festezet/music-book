#!/usr/bin/env python3
"""
Music Book Generator - Mode CLI
Gestion du catalogue de partitions et generation de livres depuis le terminal.

Usage:
    python3 cli.py list-songs [--genre GENRE] [--artist ARTIST] [--limit N]
    python3 cli.py list-books
    python3 cli.py import-folder <path> [--dry-run]
    python3 cli.py stats
    python3 cli.py search <query>
"""

import argparse
import sys
import os
from pathlib import Path

# Backend path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db
from models.song import Song
from models.book import Book
from models.book_song import BookSong


def cmd_list_songs(args):
    with app.app_context():
        query = Song.query

        if args.genre:
            query = query.filter(Song.genre.ilike(f'%{args.genre}%'))
        if args.artist:
            query = query.filter(Song.artist.ilike(f'%{args.artist}%'))

        query = query.order_by(Song.artist, Song.title)
        songs = query.limit(args.limit).all()

        if not songs:
            print("Aucune partition trouvee.")
            return

        print(f"{'ID':>4} {'Artiste':<25} {'Titre':<35} {'Genre':<20}")
        print("-" * 87)
        for s in songs:
            print(f"{s.id:>4} {(s.artist or '?')[:24]:<25} {(s.title or '?')[:34]:<35} {(s.genre or '')[:19]:<20}")

        print(f"\n{len(songs)} partition(s)")


def cmd_list_books(args):
    with app.app_context():
        books = Book.query.order_by(Book.title).all()

        if not books:
            print("Aucun livre.")
            return

        print(f"{'ID':>4} {'Titre':<35} {'Instrument':<12} {'Songs':>5}")
        print("-" * 60)
        for b in books:
            count = BookSong.query.filter_by(book_id=b.id).count()
            print(f"{b.id:>4} {(b.title or '?')[:34]:<35} {(b.instrument or '')[:11]:<12} {count:>5}")

        print(f"\n{len(books)} livre(s)")


def cmd_import_folder(args):
    folder = Path(args.path)
    if not folder.is_dir():
        print(f"Dossier non trouve: {folder}", file=sys.stderr)
        sys.exit(1)

    # Reutilise le batch_import existant
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

    pdfs = list(folder.glob('*.pdf'))
    if not pdfs:
        print(f"Aucun PDF trouve dans {folder}")
        return

    print(f"Trouve {len(pdfs)} PDF(s) dans {folder}")

    if args.dry_run:
        for pdf in pdfs:
            print(f"  [DRY-RUN] {pdf.name}")
        return

    # Import via batch_import
    from batch_import import import_pdf_file
    with app.app_context():
        imported = 0
        for pdf in pdfs:
            try:
                import_pdf_file(str(pdf))
                imported += 1
                print(f"  [OK] {pdf.name}")
            except Exception as e:
                print(f"  [ERREUR] {pdf.name}: {e}")

        print(f"\n{imported}/{len(pdfs)} importe(s)")


def cmd_stats(args):
    with app.app_context():
        total_songs = Song.query.count()
        total_books = Book.query.count()
        genres = db.session.query(Song.genre, db.func.count(Song.id)).group_by(Song.genre).order_by(db.func.count(Song.id).desc()).all()
        artists = db.session.query(Song.artist).distinct().count()

        print(f"Partitions: {total_songs}")
        print(f"Livres:     {total_books}")
        print(f"Artistes:   {artists}")
        print()
        print(f"{'Genre':<30} {'Count':>5}")
        print("-" * 37)
        for genre, count in genres:
            print(f"{(genre or 'Non classe'):<30} {count:>5}")


def cmd_search(args):
    with app.app_context():
        songs = Song.query.filter(
            db.or_(
                Song.title.ilike(f'%{args.query}%'),
                Song.artist.ilike(f'%{args.query}%')
            )
        ).order_by(Song.artist, Song.title).limit(50).all()

        if not songs:
            print(f"Aucun resultat pour '{args.query}'")
            return

        print(f"{'ID':>4} {'Artiste':<25} {'Titre':<35} {'Genre':<20}")
        print("-" * 87)
        for s in songs:
            print(f"{s.id:>4} {(s.artist or '?')[:24]:<25} {(s.title or '?')[:34]:<35} {(s.genre or '')[:19]:<20}")

        print(f"\n{len(songs)} resultat(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Music Book Generator - CLI",
        prog="cli.py"
    )
    sub = parser.add_subparsers(dest='command', required=True)

    # list-songs
    p_songs = sub.add_parser('list-songs', help='Lister les partitions')
    p_songs.add_argument('--genre', help='Filtrer par genre')
    p_songs.add_argument('--artist', help='Filtrer par artiste')
    p_songs.add_argument('--limit', type=int, default=100)

    # list-books
    sub.add_parser('list-books', help='Lister les livres')

    # import-folder
    p_import = sub.add_parser('import-folder', help='Importer des PDFs depuis un dossier')
    p_import.add_argument('path', help='Chemin du dossier')
    p_import.add_argument('--dry-run', action='store_true', help='Simulation sans import')

    # stats
    sub.add_parser('stats', help='Statistiques du catalogue')

    # search
    p_search = sub.add_parser('search', help='Rechercher par titre ou artiste')
    p_search.add_argument('query', help='Terme de recherche')

    args = parser.parse_args()
    commands = {
        'list-songs': cmd_list_songs,
        'list-books': cmd_list_books,
        'import-folder': cmd_import_folder,
        'stats': cmd_stats,
        'search': cmd_search,
    }
    commands[args.command](args)


if __name__ == '__main__':
    main()
