#!/usr/bin/env python3
"""
Extract metadata from Ultimate Guitar PDF files.
Updates songs in database with: key, difficulty, tuning.

Usage:
    python3 extract_metadata_from_pdf.py [--dry-run]
"""
import sys
import os
import re

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader


def extract_metadata_from_pdf(pdf_path: str) -> dict:
    """Extract Key, Difficulty, Tuning, YouTube link from Ultimate Guitar PDF"""
    metadata = {
        'key': None,
        'difficulty': None,
        'tuning': None,
        'youtube_url': None
    }

    try:
        reader = PdfReader(pdf_path)
        if not reader.pages:
            return metadata

        # Get first page text
        text = reader.pages[0].extract_text()
        if not text:
            return metadata

        # Extract Key (e.g., "Key: F#m", "Key: C", "Key: Am")
        key_match = re.search(r'Key:\s*([A-Ga-g][#b]?m?\d?(?:maj|min)?)', text)
        if key_match:
            metadata['key'] = key_match.group(1).strip()

        # Extract Difficulty (e.g., "Difficulty: intermediate")
        diff_match = re.search(r'Di.?culty:\s*(\w+)', text, re.IGNORECASE)
        if diff_match:
            difficulty = diff_match.group(1).lower().strip()
            # Normalize difficulty values
            if difficulty in ['beginner', 'easy', 'novice']:
                metadata['difficulty'] = 'easy'
            elif difficulty in ['intermediate', 'medium']:
                metadata['difficulty'] = 'medium'
            elif difficulty in ['advanced', 'hard', 'expert']:
                metadata['difficulty'] = 'advanced'
            else:
                metadata['difficulty'] = difficulty

        # Extract Tuning (e.g., "Tuning: E A D G B E", "Tuning: D A D G B E")
        # Standard guitar tuning is 6 notes separated by spaces
        # Each note is a single letter optionally followed by # or b
        tuning_match = re.search(r'Tuning:\s*([EADGB][#b]?)\s+([EADGB][#b]?)\s+([EADGB][#b]?)\s+([EADGB][#b]?)\s+([EADGB][#b]?)\s+([EADGB][#b]?)', text)
        if tuning_match:
            tuning = ' '.join(tuning_match.groups())
            metadata['tuning'] = tuning

        # Extract YouTube URL (various formats)
        # Pattern 1: https://www.youtube.com/watch?v=XXXXX
        # Pattern 2: https://youtu.be/XXXXX
        # Sometimes split across lines: www.youtube.com/watch?v=XXXXX
        youtube_patterns = [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'https?://youtu\.be/([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
        ]

        for pattern in youtube_patterns:
            match = re.search(pattern, text)
            if match:
                video_id = match.group(1)
                metadata['youtube_url'] = f"https://www.youtube.com/watch?v={video_id}"
                break

    except Exception as e:
        print(f"  Error reading PDF: {e}")

    return metadata


def update_song_metadata(dry_run: bool = False):
    """Update all Ultimate Guitar songs with extracted metadata"""
    from app import app, db
    from models.song import Song

    with app.app_context():
        # Get all Ultimate Guitar songs
        songs = Song.query.filter_by(source='ultimate_guitar').all()

        print(f"\n{'='*60}")
        print(f"Extracting metadata from {len(songs)} Ultimate Guitar PDFs")
        print(f"Mode: {'DRY RUN' if dry_run else 'UPDATE'}")
        print(f"{'='*60}\n")

        updated = 0
        skipped = 0
        errors = 0

        for song in songs:
            pdf_path = song.pdf_path

            if not pdf_path or not os.path.exists(pdf_path):
                print(f"[-] {song.title}: PDF not found ({pdf_path})")
                errors += 1
                continue

            metadata = extract_metadata_from_pdf(pdf_path)

            # Check if we found anything new
            changes = []
            if metadata['key'] and song.key != metadata['key']:
                changes.append(f"key={metadata['key']}")
            if metadata['difficulty'] and song.difficulty != metadata['difficulty']:
                changes.append(f"difficulty={metadata['difficulty']}")
            if metadata['tuning'] and song.tuning != metadata['tuning']:
                changes.append(f"tuning={metadata['tuning']}")
            if metadata['youtube_url'] and song.youtube_url != metadata['youtube_url']:
                changes.append(f"youtube")

            if not changes:
                skipped += 1
                continue

            print(f"[+] {song.title} - {song.artist}")
            print(f"    {', '.join(changes)}")

            if not dry_run:
                if metadata['key']:
                    song.key = metadata['key']
                if metadata['difficulty']:
                    song.difficulty = metadata['difficulty']
                if metadata['tuning']:
                    song.tuning = metadata['tuning']
                if metadata['youtube_url']:
                    song.youtube_url = metadata['youtube_url']

            updated += 1

        if not dry_run:
            db.session.commit()

        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Updated: {updated}")
        print(f"Skipped (no changes): {skipped}")
        print(f"Errors: {errors}")
        print(f"{'='*60}\n")


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    update_song_metadata(dry_run)
