"""
Constantes partagees entre les widgets Music Book.

Contient les definitions d'instruments (couleurs, labels, badges)
reutilisees par song_manager, song_library, etc.
"""

# Couleurs par instrument pour les badges CTk (light_color, dark_color)
INSTRUMENT_COLORS = {
    'guitar': ("#22c55e", "#16a34a"),   # Green
    'bass': ("#f59e0b", "#d97706"),     # Orange/Amber
    'violin': ("#8b5cf6", "#7c3aed"),   # Purple
    'piano': ("#ec4899", "#db2777"),    # Pink (song_manager) / Blue (song_library)
    'ukulele': ("#06b6d4", "#0891b2"),  # Cyan
}

# Variante song_library (piano en bleu)
INSTRUMENT_COLORS_ALT = {
    **INSTRUMENT_COLORS,
    'piano': ("#3b82f6", "#2563eb"),    # Blue variant
}

# Labels courts pour badges
INSTRUMENT_LABELS = {
    'guitar': 'GTR',
    'bass': 'BASS',
    'violin': 'VLN',
    'piano': 'PNO',
    'ukulele': 'UKE',
}

# Labels de source compacts
SOURCE_LABELS = {
    'ultimate_guitar': 'UG',
    'songsterr': 'SS',
    'boite_chansons': 'BAC',
}

# Couleur par defaut pour instrument inconnu
DEFAULT_INSTRUMENT_COLOR = ("#6b7280", "#4b5563")
