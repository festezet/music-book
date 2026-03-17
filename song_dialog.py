"""
SongDialog - Dialogue pour ajouter/editer un morceau (tkinter)
Extrait de music_book_gui.py pour modularite.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox


class SongDialog:
    """Dialogue pour ajouter/editer un morceau"""

    def __init__(self, parent, title, song_data=None):
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Frame principal
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        self._create_text_entries(frame, song_data)
        self._create_option_entries(frame, song_data)
        self._create_instrument_checkboxes(frame, song_data)
        self._create_extra_entries(frame, song_data)

        # PDF path (cache pour import)
        self.pdf_path = song_data.get('pdf_path', '') if song_data else ''

        # Boutons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="Enregistrer", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Annuler", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Attendre la fermeture
        parent.wait_window(self.dialog)

    def _create_text_entries(self, frame, song_data):
        """Create title, artist and key entry fields."""
        # Titre
        ttk.Label(frame, text="Titre *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=song_data.get('title', '') if song_data else '')
        ttk.Entry(frame, textvariable=self.title_var, width=40).grid(row=0, column=1, pady=5)

        # Artiste
        ttk.Label(frame, text="Artiste").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.artist_var = tk.StringVar(value=song_data.get('artist', '') if song_data else '')
        ttk.Entry(frame, textvariable=self.artist_var, width=40).grid(row=1, column=1, pady=5)

        # Tonalite
        ttk.Label(frame, text="Tonalite").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.key_var = tk.StringVar(value=song_data.get('key', '') if song_data else '')
        ttk.Entry(frame, textvariable=self.key_var, width=40).grid(row=2, column=1, pady=5)

    def _create_option_entries(self, frame, song_data):
        """Create tempo, genre and difficulty fields."""
        # Tempo
        ttk.Label(frame, text="Tempo (BPM)").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.tempo_var = tk.StringVar(value=str(song_data.get('tempo', '')) if song_data and song_data.get('tempo') else '')
        ttk.Entry(frame, textvariable=self.tempo_var, width=40).grid(row=3, column=1, pady=5)

        # Genre
        ttk.Label(frame, text="Genre").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.genre_var = tk.StringVar(value=song_data.get('genre', '') if song_data else '')
        ttk.Entry(frame, textvariable=self.genre_var, width=40).grid(row=4, column=1, pady=5)

        # Difficulte
        ttk.Label(frame, text="Difficulte").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.difficulty_var = tk.StringVar(value=song_data.get('difficulty', '') if song_data else '')
        ttk.Combobox(frame, textvariable=self.difficulty_var,
                    values=["", "easy", "medium", "advanced"], width=37).grid(row=5, column=1, pady=5)

    def _create_instrument_checkboxes(self, frame, song_data):
        """Create instrument checkbox fields."""
        ttk.Label(frame, text="Instruments").grid(row=6, column=0, sticky=tk.W, pady=5)
        instruments_frame = ttk.Frame(frame)
        instruments_frame.grid(row=6, column=1, sticky=tk.W, pady=5)

        self.guitar_var = tk.BooleanVar(value='guitar' in song_data.get('instruments', []) if song_data else False)
        self.bass_var = tk.BooleanVar(value='bass' in song_data.get('instruments', []) if song_data else False)
        self.violin_var = tk.BooleanVar(value='violin' in song_data.get('instruments', []) if song_data else False)

        ttk.Checkbutton(instruments_frame, text="Guitare", variable=self.guitar_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(instruments_frame, text="Basse", variable=self.bass_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(instruments_frame, text="Violon", variable=self.violin_var).pack(side=tk.LEFT, padx=5)

    def _create_extra_entries(self, frame, song_data):
        """Create pages and notes fields."""
        # Pages
        ttk.Label(frame, text="Nombre de pages").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.pages_var = tk.StringVar(value=str(song_data.get('pages', '')) if song_data and song_data.get('pages') else '')
        ttk.Entry(frame, textvariable=self.pages_var, width=40).grid(row=7, column=1, pady=5)

        # Notes
        ttk.Label(frame, text="Notes").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.notes_text = tk.Text(frame, width=40, height=5)
        self.notes_text.grid(row=8, column=1, pady=5)
        if song_data and song_data.get('notes'):
            self.notes_text.insert('1.0', song_data['notes'])

    def save(self):
        """Sauvegarder les donnees"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Attention", "Le titre est obligatoire")
            return

        # Collecter instruments
        instruments = []
        if self.guitar_var.get():
            instruments.append('guitar')
        if self.bass_var.get():
            instruments.append('bass')
        if self.violin_var.get():
            instruments.append('violin')

        # PDF path
        pdf_path = self.pdf_path or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'pdfs', f'placeholder_{title.replace(" ", "_")}.pdf')

        self.result = {
            'title': title,
            'artist': self.artist_var.get().strip() or None,
            'key': self.key_var.get().strip() or None,
            'tempo': int(self.tempo_var.get()) if self.tempo_var.get().strip() else None,
            'genre': self.genre_var.get().strip() or None,
            'difficulty': self.difficulty_var.get() or None,
            'instruments': instruments,
            'pages': int(self.pages_var.get()) if self.pages_var.get().strip() else None,
            'notes': self.notes_text.get('1.0', tk.END).strip() or None,
            'pdf_path': pdf_path
        }

        self.dialog.destroy()
