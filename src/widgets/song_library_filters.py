"""
Song Library Filters - Filter, sort and option change logic.
Extracted from song_library.py for modularity.
"""
from typing import Dict, List


def sort_songs(songs: List[Dict], sort_key: str) -> List[Dict]:
    """Sort songs by specified key"""
    if sort_key == "title_asc":
        return sorted(songs, key=lambda s: s['title'].lower())
    elif sort_key == "title_desc":
        return sorted(songs, key=lambda s: s['title'].lower(), reverse=True)
    elif sort_key == "artist_asc":
        return sorted(songs, key=lambda s: s['artist'].lower())
    elif sort_key == "artist_desc":
        return sorted(songs, key=lambda s: s['artist'].lower(), reverse=True)
    elif sort_key == "genre":
        return sorted(songs, key=lambda s: s['genre'].lower())
    elif sort_key == "source":
        return sorted(songs, key=lambda s: s['source'].lower())
    return songs


def filter_songs(all_songs: List[Dict], **filters) -> List[Dict]:
    """Apply search and filters to the song list.

    Keyword args:
        search: Search text (lowercased).
        instrument: Instrument filter value (empty = all).
        source: Source filter value (empty = all).
        genre: Genre filter value ("Tous" = all).
        artist: Artist filter value ("Tous" = all).
    """
    search = filters.get('search', '')
    instrument = filters.get('instrument', '')
    source = filters.get('source', '')
    genre = filters.get('genre', '')
    artist = filters.get('artist', '')

    filtered = []
    for song in all_songs:
        if search:
            if search not in song['title'].lower() and search not in song['artist'].lower():
                continue
        if instrument and instrument not in song['instruments']:
            continue
        if source and song['source'] != source:
            continue
        if genre and genre != "Tous" and song['genre'] != genre:
            continue
        if artist and artist != "Tous" and song['artist'] != artist:
            continue
        filtered.append(song)
    return filtered


def resolve_option_value(choice: str, options: list) -> str:
    """Map a display label to its option value."""
    for label, value in options:
        if label == choice:
            return value
    return ""


def get_add_all_sort_key(song: Dict):
    """Sort key for 'add all': artist last name, then title."""
    artist = song.get('artist', '').strip()
    if artist:
        surname = artist.split()[-1].lower()
    else:
        surname = ''
    title = song.get('title', '').lower()
    return (surname, title)
