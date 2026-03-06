#!/usr/bin/env python3
"""
Script d'import automatique des fichiers PDF de chords/tabs
Extrait les métadonnées à partir du nom de fichier

Sources supportées :
- Ultimate Guitar : "{Titre} Chords by {Artiste}tabs @ Ultimate Guitar Archive.pdf"
- Songsterr : "{Titre} [Bass ]Tab by {Artiste} _ Songsterr Tabs with Rhythm_{instrument}.pdf"
- La Boîte à chansons : "{Titre} - {Artiste} - La Boîte à chansons.pdf"

Usage:
    python3 import_chords_folder.py [dossier] [--dry-run] [--clean]

Options:
    --dry-run : Affiche ce qui serait importé sans modifier la BDD
    --clean   : Nettoie la BDD avant import (supprime tous les morceaux)
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db
from models.song import Song

# =============================================================================
# REGEX PATTERNS
# =============================================================================

# Ultimate Guitar: "Hey Joe Chords by Jimi Hendrixtabs @ Ultimate Guitar Archive.pdf"
# Note: "tabs" est collé à l'artiste (bug de formatage Ultimate Guitar)
PATTERN_ULTIMATE_GUITAR = re.compile(
    r'^(?P<title>.+?)\s+Chords\s+by\s+(?P<artist>.+?)tabs\s+@\s+Ultimate\s+Guitar\s+Archive\.pdf$',
    re.IGNORECASE
)

# Songsterr Guitar: "Hey Joe Tab by Jimi Hendrix _ Songsterr Tabs with Rhythm_guitare.pdf"
# Songsterr Bass: "Hey Joe Bass Tab by Jimi Hendrix _ Songsterr Tabs with Rhythm_bass.pdf"
PATTERN_SONGSTERR = re.compile(
    r'^(?P<title>.+?)\s+(?P<type>Bass\s+)?Tab\s+by\s+(?P<artist>.+?)\s+_\s+Songsterr\s+Tabs\s+with\s+Rhythm_(?P<instrument>\w+)\.pdf$',
    re.IGNORECASE
)

# La Boîte à chansons: "Mistral Gagnant - Renaud - La Boîte à chansons.pdf"
PATTERN_BOITE_CHANSONS = re.compile(
    r'^(?P<title>.+?)\s+-\s+(?P<artist>.+?)\s+-\s+La\s+Bo[îi]te\s+[àa]\s+chansons\.pdf$',
    re.IGNORECASE
)


# =============================================================================
# PARSING FUNCTIONS
# =============================================================================

def parse_ultimate_guitar(filename: str) -> dict | None:
    """Parse un nom de fichier Ultimate Guitar"""
    match = PATTERN_ULTIMATE_GUITAR.match(filename)
    if not match:
        return None

    return {
        'title': match.group('title').strip(),
        'artist': match.group('artist').strip(),
        'source': 'ultimate_guitar',
        'instruments': ['guitar'],  # Ultimate Guitar = principalement guitare
        'type': 'chords'
    }


def parse_songsterr(filename: str) -> dict | None:
    """Parse un nom de fichier Songsterr"""
    match = PATTERN_SONGSTERR.match(filename)
    if not match:
        return None

    # Déterminer l'instrument
    instrument_raw = match.group('instrument').lower()
    is_bass_tab = match.group('type') is not None  # "Bass Tab" dans le titre

    # Mapping des instruments
    instrument_map = {
        'guitare': 'guitar',
        'guitar': 'guitar',
        'bass': 'bass',
        'basse': 'bass',
        'violin': 'violin',
        'violon': 'violin'
    }

    instrument = instrument_map.get(instrument_raw, instrument_raw)

    # Si "Bass Tab" est dans le titre, c'est forcément basse
    if is_bass_tab:
        instrument = 'bass'

    return {
        'title': match.group('title').strip(),
        'artist': match.group('artist').strip(),
        'source': 'songsterr',
        'instruments': [instrument],
        'type': 'tab'
    }


def parse_boite_chansons(filename: str) -> dict | None:
    """Parse un nom de fichier La Boîte à chansons"""
    match = PATTERN_BOITE_CHANSONS.match(filename)
    if not match:
        return None

    return {
        'title': match.group('title').strip(),
        'artist': match.group('artist').strip(),
        'source': 'boite_chansons',
        'instruments': ['guitar'],  # La Boîte à chansons = principalement guitare
        'type': 'chords'
    }


def parse_filename(filename: str) -> dict | None:
    """
    Parse un nom de fichier et extrait les métadonnées
    Retourne None si le pattern n'est pas reconnu
    """
    # Essayer Ultimate Guitar
    result = parse_ultimate_guitar(filename)
    if result:
        return result

    # Essayer Songsterr
    result = parse_songsterr(filename)
    if result:
        return result

    # Essayer La Boîte à chansons
    result = parse_boite_chansons(filename)
    if result:
        return result

    return None


def get_pdf_page_count(pdf_path: str) -> int | None:
    """Obtenir le nombre de pages d'un PDF"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception as e:
        print(f"  ⚠️  Erreur lecture PDF: {e}")
        return None


# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

def clean_database():
    """Supprime tous les morceaux de la base de données"""
    with app.app_context():
        count = Song.query.count()
        Song.query.delete()
        db.session.commit()
        return count


def song_exists(title: str, artist: str, instrument: str) -> bool:
    """Vérifie si un morceau existe déjà (même titre + artiste + instrument)"""
    with app.app_context():
        existing = Song.query.filter(
            Song.title == title,
            Song.artist == artist
        ).all()

        for song in existing:
            instruments = json.loads(song.instruments) if song.instruments else []
            if instrument in instruments:
                return True

        return False


def add_song(metadata: dict, pdf_path: str, pages: int = None) -> Song:
    """Ajoute un morceau à la base de données"""
    with app.app_context():
        song = Song(
            title=metadata['title'],
            artist=metadata['artist'],
            instruments=json.dumps(metadata['instruments']),
            pdf_path=pdf_path,
            pages=pages,
            source=metadata['source'],
            type=metadata['type']
        )
        db.session.add(song)
        db.session.commit()
        return song.id


# =============================================================================
# MAIN IMPORT FUNCTION
# =============================================================================

def import_folder(folder_path: str, dry_run: bool = False, clean: bool = False) -> dict:
    """
    Importe tous les PDF d'un dossier

    Args:
        folder_path: Chemin du dossier à scanner
        dry_run: Si True, affiche sans modifier la BDD
        clean: Si True, nettoie la BDD avant import

    Returns:
        Statistiques d'import
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise ValueError(f"Dossier non trouvé: {folder_path}")

    # Statistiques
    stats = {
        'total_files': 0,
        'imported': 0,
        'skipped_duplicate': 0,
        'skipped_unknown': 0,
        'errors': 0,
        'cleaned': 0,
        'by_source': {'ultimate_guitar': 0, 'songsterr': 0, 'boite_chansons': 0},
        'by_instrument': {'guitar': 0, 'bass': 0, 'violin': 0}
    }

    # Nettoyer la BDD si demandé
    if clean and not dry_run:
        stats['cleaned'] = clean_database()
        print(f"\n🗑️  Base de données nettoyée: {stats['cleaned']} morceaux supprimés\n")
    elif clean and dry_run:
        with app.app_context():
            stats['cleaned'] = Song.query.count()
        print(f"\n🗑️  [DRY-RUN] Suppression de {stats['cleaned']} morceaux\n")

    # Scanner les fichiers
    pdf_files = list(folder.glob('*.pdf'))
    stats['total_files'] = len(pdf_files)

    print(f"📂 Dossier: {folder_path}")
    print(f"📄 Fichiers PDF trouvés: {stats['total_files']}\n")
    print("=" * 80)

    for pdf_file in sorted(pdf_files):
        filename = pdf_file.name
        print(f"\n📄 {filename}")

        # Parser le nom de fichier
        metadata = parse_filename(filename)

        if not metadata:
            print(f"   ❌ Pattern non reconnu")
            stats['skipped_unknown'] += 1
            continue

        # Afficher les métadonnées extraites
        print(f"   ✅ Source: {metadata['source']}")
        print(f"   📝 Titre: {metadata['title']}")
        print(f"   🎤 Artiste: {metadata['artist']}")
        print(f"   🎸 Instruments: {', '.join(metadata['instruments'])}")
        print(f"   📋 Type: {metadata['type']}")

        # Vérifier si existe déjà
        instrument = metadata['instruments'][0] if metadata['instruments'] else 'guitar'

        if not dry_run and not clean:
            if song_exists(metadata['title'], metadata['artist'], instrument):
                print(f"   ⏭️  Déjà en base (ignoré)")
                stats['skipped_duplicate'] += 1
                continue

        # Compter les pages
        pages = get_pdf_page_count(str(pdf_file))
        if pages:
            print(f"   📖 Pages: {pages}")

        # Importer
        if not dry_run:
            try:
                song_id = add_song(metadata, str(pdf_file), pages)
                print(f"   ✅ Importé (ID: {song_id})")
                stats['imported'] += 1
                stats['by_source'][metadata['source']] += 1
                for inst in metadata['instruments']:
                    if inst in stats['by_instrument']:
                        stats['by_instrument'][inst] += 1
            except Exception as e:
                print(f"   ❌ Erreur: {e}")
                stats['errors'] += 1
        else:
            print(f"   ⏸️  [DRY-RUN] Serait importé")
            stats['imported'] += 1
            stats['by_source'][metadata['source']] += 1
            for inst in metadata['instruments']:
                if inst in stats['by_instrument']:
                    stats['by_instrument'][inst] += 1

    return stats


def print_stats(stats: dict, dry_run: bool = False):
    """Affiche les statistiques d'import"""
    print("\n" + "=" * 80)
    print("📊 RÉSUMÉ DE L'IMPORT" + (" [DRY-RUN]" if dry_run else ""))
    print("=" * 80)

    if stats['cleaned'] > 0:
        print(f"🗑️  Morceaux supprimés: {stats['cleaned']}")

    print(f"📄 Total fichiers scannés: {stats['total_files']}")
    print(f"✅ Importés: {stats['imported']}")
    print(f"⏭️  Ignorés (doublons): {stats['skipped_duplicate']}")
    print(f"❌ Non reconnus: {stats['skipped_unknown']}")
    print(f"⚠️  Erreurs: {stats['errors']}")

    print(f"\n📦 Par source:")
    print(f"   - Ultimate Guitar: {stats['by_source']['ultimate_guitar']}")
    print(f"   - Songsterr: {stats['by_source']['songsterr']}")
    print(f"   - La Boîte à chansons: {stats['by_source']['boite_chansons']}")

    print(f"\n🎸 Par instrument:")
    print(f"   - Guitare: {stats['by_instrument']['guitar']}")
    print(f"   - Basse: {stats['by_instrument']['bass']}")
    print(f"   - Violon: {stats['by_instrument']['violin']}")

    # Vérifier la base
    with app.app_context():
        total_in_db = Song.query.count()
    print(f"\n📚 Total en base de données: {total_in_db} morceaux")


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Import automatique de fichiers PDF de chords/tabs"
    )
    parser.add_argument(
        'folder',
        nargs='?',
        default='/home/fabrice-ryzen/Downloads/Chords',
        help="Dossier contenant les PDF (défaut: ~/Downloads/Chords)"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Affiche ce qui serait importé sans modifier la BDD"
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help="Nettoie la BDD avant import (supprime tous les morceaux)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🎵 MUSIC BOOK - Import automatique de Chords/Tabs")
    print("=" * 80)

    if args.dry_run:
        print("⚠️  Mode DRY-RUN activé (aucune modification)")

    if args.clean:
        print("⚠️  Mode CLEAN activé (suppression avant import)")

    try:
        stats = import_folder(args.folder, args.dry_run, args.clean)
        print_stats(stats, args.dry_run)

        if args.dry_run:
            print("\n💡 Relancez sans --dry-run pour effectuer l'import réel")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
