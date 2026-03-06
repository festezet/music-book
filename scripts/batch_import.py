#!/usr/bin/env python3
"""
Batch Import Script for Music Book Generator
Imports PDF files from a folder with automatic metadata extraction.

Usage:
    python3 batch_import.py /path/to/folder [--dry-run]
"""
import sys
import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# French artists -> Chanson Francaise
CHANSON_FRANCAISE_ARTISTS = {
    'georges brassens': 'Chanson Francaise',
    'serge gainsbourg': 'Chanson Francaise',
    'michel berger': 'Chanson Francaise',
    'nino ferrer': 'Chanson Francaise',
    'renaud': 'Chanson Francaise',
    'pierre perret': 'Chanson Francaise',
    'claude nougaro': 'Chanson Francaise',
    'bernard lavilliers': 'Chanson Francaise',
    'henri salvador': 'Chanson Francaise',
    'telephone': 'Chanson Francaise',
    'téléphone': 'Chanson Francaise',
    'mano solo': 'Chanson Francaise',
    'les rita mitsouko': 'Chanson Francaise',
}

# Genre mapping for other known artists
OTHER_ARTISTS_GENRES = {
    'jimi hendrix': 'Rock',
    'the rolling stones': 'Rock',
    'radiohead': 'Rock',
    'ac/dc': 'Rock',
    'ac_dc': 'Rock',
}


def detect_source(filename: str) -> str:
    """Detect source from filename pattern"""
    filename_lower = filename.lower()

    if 'ultimate guitar' in filename_lower or 'tabs @' in filename_lower:
        return 'ultimate_guitar'
    elif 'songsterr' in filename_lower:
        return 'songsterr'
    elif 'boîte à chansons' in filename_lower or 'boite a chansons' in filename_lower:
        return 'boite_chansons'

    return 'ultimate_guitar'  # Default


def detect_type(filename: str) -> str:
    """Detect type (chords/tab) from filename"""
    filename_lower = filename.lower()

    if ' tab ' in filename_lower or ' tab.' in filename_lower or '_tab' in filename_lower:
        return 'tab'
    elif 'chords' in filename_lower:
        return 'chords'

    return 'chords'  # Default


def detect_instrument(filename: str) -> str:
    """Detect instrument from filename"""
    filename_lower = filename.lower()

    if '_bass' in filename_lower or 'bass tab' in filename_lower:
        return 'bass'
    elif '_violin' in filename_lower or 'violin' in filename_lower:
        return 'violin'
    elif '_guitare' in filename_lower or '_guitar' in filename_lower:
        return 'guitar'

    return 'guitar'  # Default for chords


def parse_ultimate_guitar_filename(filename: str) -> dict:
    """
    Parse Ultimate Guitar filename pattern:
    'Title Chords (ver N) by Artisttabs @ Ultimate Guitar Archive.pdf'
    'Title Chords by Artisttabs @ Ultimate Guitar Archive.pdf'
    """
    # Remove extension
    name = filename.replace('.pdf', '')

    # Pattern: Title Chords/Tab (ver X) by Artist tabs @ UG
    patterns = [
        # With version: "Title Chords (ver 3) by Artisttabs @ UG"
        r'^(.+?)\s+(?:Chords|Tab)\s*\(ver\s*\d+\)\s*by\s+(.+?)tabs\s*@\s*Ultimate',
        # Without version: "Title Chords by Artisttabs @ UG"
        r'^(.+?)\s+(?:Chords|Tab)\s+by\s+(.+?)tabs\s*@\s*Ultimate',
        # Tab version: "Title Tab (ver 3) by Artisttabs @ UG"
        r'^(.+?)\s+Tab\s*\(ver\s*\d+\)\s*by\s+(.+?)tabs\s*@\s*Ultimate',
    ]

    for pattern in patterns:
        match = re.match(pattern, name, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            artist = match.group(2).strip()
            return {'title': title, 'artist': artist}

    return None


def parse_songsterr_filename(filename: str) -> dict:
    """
    Parse Songsterr filename pattern:
    'Title Tab by Artist _ Songsterr Tabs with Rhythm.pdf'
    'Title Bass Tab by Artist _ Songsterr Tabs with Rhythm_bass.pdf'
    'Title - Artist - Instrument details _ Songsterr...'
    """
    name = filename.replace('.pdf', '')

    # Remove instrument suffix
    name = re.sub(r'_(bass|guitar|guitare|violin)$', '', name, flags=re.IGNORECASE)

    # Pattern 1: "Title Tab/Bass Tab by Artist _ Songsterr"
    patterns = [
        r'^(.+?)\s+(?:Bass\s+)?Tab\s+by\s+(.+?)\s*_\s*Songsterr',
    ]

    for pattern in patterns:
        match = re.match(pattern, name, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            artist = match.group(2).strip()
            # Clean artist: remove instrument details after " - "
            # e.g. "AC_DC - Malcolm Young Rhythm..." -> "AC_DC"
            if ' - ' in artist:
                parts = artist.split(' - ')
                # First part is usually the artist
                artist = parts[0].strip()
                # Replace underscore with slash for AC/DC style
                artist = artist.replace('_', '/')
            return {'title': title, 'artist': artist}

    return None


def parse_boite_chansons_filename(filename: str) -> dict:
    """
    Parse Boîte à chansons filename pattern:
    'Title - Artist - La Boîte à chansons.pdf'
    """
    name = filename.replace('.pdf', '')

    # Pattern: "Title - Artist - La Boîte à chansons"
    match = re.match(r'^(.+?)\s*-\s*(.+?)\s*-\s*La Boîte', name, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        artist = match.group(2).strip()
        return {'title': title, 'artist': artist}

    return None


def parse_filename(filename: str) -> dict:
    """Parse filename to extract metadata"""
    source = detect_source(filename)

    result = None
    if source == 'ultimate_guitar':
        result = parse_ultimate_guitar_filename(filename)
    elif source == 'songsterr':
        result = parse_songsterr_filename(filename)
    elif source == 'boite_chansons':
        result = parse_boite_chansons_filename(filename)

    if not result:
        # Fallback: try to extract something
        name = filename.replace('.pdf', '')
        name = re.sub(r'\s*[@_-]\s*(Ultimate|Songsterr|Boîte|La Boîte).*', '', name, flags=re.IGNORECASE)
        result = {'title': name, 'artist': ''}

    # Add detected metadata
    result['source'] = source
    result['type'] = detect_type(filename)
    result['instrument'] = detect_instrument(filename)

    # Detect genre from artist
    artist_lower = result['artist'].lower()
    if artist_lower in CHANSON_FRANCAISE_ARTISTS:
        result['genre'] = CHANSON_FRANCAISE_ARTISTS[artist_lower]
    elif artist_lower in OTHER_ARTISTS_GENRES:
        result['genre'] = OTHER_ARTISTS_GENRES[artist_lower]
    else:
        result['genre'] = ''

    return result


def check_duplicate(title: str, artist: str, instrument: str) -> bool:
    """Check if song already exists in database"""
    from app import app, db
    from models.song import Song

    with app.app_context():
        existing = Song.query.filter(
            Song.title.ilike(title),
            Song.artist.ilike(artist) if artist else True
        ).all()

        for song in existing:
            instruments = json.loads(song.instruments) if song.instruments else []
            if instrument in instruments:
                return True

    return False


def import_file(filepath: Path, dest_folder: Path, dry_run: bool = False) -> dict:
    """Import a single file"""
    filename = filepath.name
    metadata = parse_filename(filename)

    # Check for duplicate
    is_duplicate = check_duplicate(
        metadata['title'],
        metadata['artist'],
        metadata['instrument']
    )

    if is_duplicate:
        return {
            'status': 'skipped',
            'reason': 'duplicate',
            'filename': filename,
            'metadata': metadata
        }

    if dry_run:
        return {
            'status': 'would_import',
            'filename': filename,
            'metadata': metadata
        }

    # Copy file to destination
    instrument_folder = dest_folder / metadata['instrument']
    instrument_folder.mkdir(parents=True, exist_ok=True)

    dest_path = instrument_folder / filename
    shutil.copy2(filepath, dest_path)

    # Insert into database
    from app import app, db
    from models.song import Song

    with app.app_context():
        song = Song(
            title=metadata['title'],
            artist=metadata['artist'],
            genre=metadata['genre'],
            instruments=json.dumps([metadata['instrument']]),
            source=metadata['source'],
            type=metadata['type'],
            pdf_path=str(dest_path),
            pages=1,  # Default, could extract from PDF
        )
        db.session.add(song)
        db.session.commit()

    return {
        'status': 'imported',
        'filename': filename,
        'metadata': metadata,
        'dest_path': str(dest_path)
    }


def batch_import(source_folder: str, dry_run: bool = False):
    """Import all PDF files from folder"""
    source_path = Path(source_folder)
    dest_folder = Path('/data/projects/music-book/data/pdfs')

    if not source_path.exists():
        print(f"Error: Folder not found: {source_folder}")
        return

    pdf_files = list(source_path.glob('*.pdf'))
    print(f"\n{'=' * 60}")
    print(f"Music Book Batch Import")
    print(f"{'=' * 60}")
    print(f"Source: {source_folder}")
    print(f"Found: {len(pdf_files)} PDF files")
    print(f"Mode: {'DRY RUN' if dry_run else 'IMPORT'}")
    print(f"{'=' * 60}\n")

    results = {
        'imported': [],
        'skipped': [],
        'would_import': [],
        'errors': []
    }

    for pdf_file in sorted(pdf_files):
        try:
            result = import_file(pdf_file, dest_folder, dry_run)
            status = result['status']

            if status == 'imported':
                results['imported'].append(result)
                print(f"[+] {result['metadata']['title']} - {result['metadata']['artist']}")
                print(f"    Genre: {result['metadata']['genre'] or 'N/A'} | Instrument: {result['metadata']['instrument']}")
            elif status == 'skipped':
                results['skipped'].append(result)
                print(f"[-] SKIP (duplicate): {result['metadata']['title']} - {result['metadata']['artist']}")
            elif status == 'would_import':
                results['would_import'].append(result)
                print(f"[?] Would import: {result['metadata']['title']} - {result['metadata']['artist']}")
                print(f"    Genre: {result['metadata']['genre'] or 'N/A'} | Instrument: {result['metadata']['instrument']}")

        except Exception as e:
            results['errors'].append({'filename': pdf_file.name, 'error': str(e)})
            print(f"[!] ERROR: {pdf_file.name}: {e}")

    # Summary
    print(f"\n{'=' * 60}")
    print("SUMMARY")
    print(f"{'=' * 60}")
    if dry_run:
        print(f"Would import: {len(results['would_import'])}")
    else:
        print(f"Imported: {len(results['imported'])}")
    print(f"Skipped (duplicates): {len(results['skipped'])}")
    print(f"Errors: {len(results['errors'])}")
    print(f"{'=' * 60}\n")

    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 batch_import.py /path/to/folder [--dry-run]")
        sys.exit(1)

    folder = sys.argv[1]
    dry_run = '--dry-run' in sys.argv

    batch_import(folder, dry_run)
