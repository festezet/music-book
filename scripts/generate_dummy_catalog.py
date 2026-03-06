#!/usr/bin/env python3
"""
Génération de catalogue de test pour Music Book Generator
"""

import sys
import os

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app import app, db
from models.song import Song
import json

# Données de test
DUMMY_SONGS = [
    # Guitare - Facile
    {"title": "Wonderwall", "artist": "Oasis", "key": "Em", "tempo": 87, "genre": "Rock", "difficulty": "easy", "instruments": ["guitar"], "pages": 2},
    {"title": "Knocking on Heaven's Door", "artist": "Bob Dylan", "key": "G", "tempo": 68, "genre": "Folk", "difficulty": "easy", "instruments": ["guitar"], "pages": 2},
    {"title": "Horse with No Name", "artist": "America", "key": "Em", "tempo": 123, "genre": "Folk Rock", "difficulty": "easy", "instruments": ["guitar"], "pages": 2},
    {"title": "Stand by Me", "artist": "Ben E. King", "key": "A", "tempo": 118, "genre": "Soul", "difficulty": "easy", "instruments": ["guitar", "bass"], "pages": 2},
    {"title": "Let It Be", "artist": "The Beatles", "key": "C", "tempo": 72, "genre": "Rock", "difficulty": "easy", "instruments": ["guitar", "bass"], "pages": 3},

    # Guitare - Moyen
    {"title": "Hotel California", "artist": "Eagles", "key": "Bm", "tempo": 74, "genre": "Rock", "difficulty": "medium", "instruments": ["guitar"], "pages": 4},
    {"title": "Blackbird", "artist": "The Beatles", "key": "G", "tempo": 92, "genre": "Folk", "difficulty": "medium", "instruments": ["guitar"], "pages": 3},
    {"title": "Tears in Heaven", "artist": "Eric Clapton", "key": "A", "tempo": 80, "genre": "Ballad", "difficulty": "medium", "instruments": ["guitar"], "pages": 3},
    {"title": "Stairway to Heaven", "artist": "Led Zeppelin", "key": "Am", "tempo": 82, "genre": "Rock", "difficulty": "medium", "instruments": ["guitar"], "pages": 6},
    {"title": "Nothing Else Matters", "artist": "Metallica", "key": "Em", "tempo": 141, "genre": "Metal", "difficulty": "medium", "instruments": ["guitar"], "pages": 5},

    # Guitare - Avancé
    {"title": "Cliffs of Dover", "artist": "Eric Johnson", "key": "Gm", "tempo": 180, "genre": "Instrumental Rock", "difficulty": "advanced", "instruments": ["guitar"], "pages": 8},
    {"title": "Eruption", "artist": "Van Halen", "key": "Am", "tempo": 102, "genre": "Hard Rock", "difficulty": "advanced", "instruments": ["guitar"], "pages": 3},
    {"title": "Little Wing", "artist": "Jimi Hendrix", "key": "Em", "tempo": 66, "genre": "Rock", "difficulty": "advanced", "instruments": ["guitar"], "pages": 4},
    {"title": "Classical Gas", "artist": "Mason Williams", "key": "Am", "tempo": 160, "genre": "Classical", "difficulty": "advanced", "instruments": ["guitar"], "pages": 7},

    # Basse
    {"title": "Come Together", "artist": "The Beatles", "key": "Dm", "tempo": 81, "genre": "Rock", "difficulty": "medium", "instruments": ["bass", "guitar"], "pages": 3},
    {"title": "Another One Bites the Dust", "artist": "Queen", "key": "Em", "tempo": 110, "genre": "Rock", "difficulty": "easy", "instruments": ["bass"], "pages": 2},
    {"title": "Seven Nation Army", "artist": "The White Stripes", "key": "E", "tempo": 124, "genre": "Rock", "difficulty": "easy", "instruments": ["bass", "guitar"], "pages": 2},
    {"title": "Billie Jean", "artist": "Michael Jackson", "key": "F#m", "tempo": 117, "genre": "Pop", "difficulty": "medium", "instruments": ["bass"], "pages": 3},
    {"title": "Feel Good Inc.", "artist": "Gorillaz", "key": "Em", "tempo": 138, "genre": "Alternative", "difficulty": "medium", "instruments": ["bass"], "pages": 4},
    {"title": "Portrait of Tracy", "artist": "Jaco Pastorius", "key": "E", "tempo": 60, "genre": "Jazz", "difficulty": "advanced", "instruments": ["bass"], "pages": 5},

    # Violon - Classique
    {"title": "Canon in D", "artist": "Pachelbel", "key": "D", "tempo": 54, "genre": "Classical", "difficulty": "medium", "instruments": ["violin"], "pages": 4},
    {"title": "The Four Seasons - Spring", "artist": "Vivaldi", "key": "E", "tempo": 120, "genre": "Classical", "difficulty": "advanced", "instruments": ["violin"], "pages": 12},
    {"title": "Ave Maria", "artist": "Schubert", "key": "Bb", "tempo": 60, "genre": "Classical", "difficulty": "medium", "instruments": ["violin"], "pages": 3},
    {"title": "Meditation from Thaïs", "artist": "Massenet", "key": "D", "tempo": 66, "genre": "Classical", "difficulty": "advanced", "instruments": ["violin"], "pages": 5},

    # Violon - Moderne
    {"title": "Smooth Criminal", "artist": "Michael Jackson", "key": "Am", "tempo": 118, "genre": "Pop", "difficulty": "medium", "instruments": ["violin"], "pages": 3},
    {"title": "He's a Pirate", "artist": "Klaus Badelt", "key": "Dm", "tempo": 170, "genre": "Soundtrack", "difficulty": "medium", "instruments": ["violin"], "pages": 4},
    {"title": "Crystallize", "artist": "Lindsey Stirling", "key": "Em", "tempo": 140, "genre": "Electronic", "difficulty": "advanced", "instruments": ["violin"], "pages": 5},

    # Multi-instruments
    {"title": "Hallelujah", "artist": "Leonard Cohen", "key": "C", "tempo": 60, "genre": "Folk", "difficulty": "easy", "instruments": ["guitar", "violin"], "pages": 3},
    {"title": "Shape of You", "artist": "Ed Sheeran", "key": "C#m", "tempo": 96, "genre": "Pop", "difficulty": "easy", "instruments": ["guitar", "bass"], "pages": 2},
    {"title": "Smoke on the Water", "artist": "Deep Purple", "key": "Gm", "tempo": 112, "genre": "Rock", "difficulty": "easy", "instruments": ["guitar", "bass"], "pages": 3},
    {"title": "Sweet Child O' Mine", "artist": "Guns N' Roses", "key": "D", "tempo": 125, "genre": "Rock", "difficulty": "medium", "instruments": ["guitar", "bass"], "pages": 5},
]


def generate_catalog():
    """Générer le catalogue de test"""
    with app.app_context():
        # Vérifier si des données existent déjà
        existing_count = Song.query.count()
        if existing_count > 0:
            print(f"⚠️  La base contient déjà {existing_count} morceaux")
            response = input("Voulez-vous réinitialiser ? (y/N) ")
            if response.lower() != 'y':
                print("Annulé")
                return

            # Supprimer tous les morceaux
            db.session.query(Song).delete()
            db.session.commit()
            print("✅ Base de données réinitialisée")

        # Créer les morceaux
        for song_data in DUMMY_SONGS:
            song = Song(
                title=song_data['title'],
                artist=song_data['artist'],
                key=song_data.get('key'),
                tempo=song_data.get('tempo'),
                genre=song_data.get('genre'),
                difficulty=song_data.get('difficulty'),
                instruments=json.dumps(song_data.get('instruments', [])),
                pages=song_data.get('pages', 1),
                pdf_path=f"/data/projects/music-book/data/pdfs/placeholder_{song_data['title'].replace(' ', '_')}.pdf"
            )
            db.session.add(song)

        db.session.commit()
        print(f"\n✅ {len(DUMMY_SONGS)} morceaux ajoutés au catalogue")

        # Statistiques
        guitar_count = Song.query.filter(Song.instruments.contains('"guitar"')).count()
        bass_count = Song.query.filter(Song.instruments.contains('"bass"')).count()
        violin_count = Song.query.filter(Song.instruments.contains('"violin"')).count()

        print("\n📊 Statistiques:")
        print(f"   - Guitare: {guitar_count} morceaux")
        print(f"   - Basse: {bass_count} morceaux")
        print(f"   - Violon: {violin_count} morceaux")

        easy_count = Song.query.filter(Song.difficulty == 'easy').count()
        medium_count = Song.query.filter(Song.difficulty == 'medium').count()
        advanced_count = Song.query.filter(Song.difficulty == 'advanced').count()

        print(f"\n   - Facile: {easy_count}")
        print(f"   - Moyen: {medium_count}")
        print(f"   - Avancé: {advanced_count}")


if __name__ == '__main__':
    print("=" * 50)
    print("  Music Book Generator - Génération de catalogue")
    print("=" * 50)
    print()

    generate_catalog()

    print("\n🚀 Lancez l'application avec: ./start.sh")
    print("   Puis ouvrez: http://localhost:5051/catalog")
