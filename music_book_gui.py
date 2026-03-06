#!/usr/bin/env python3
"""
Music Book Generator - Interface GUI Tkinter
Application desktop pour créer des livres de partitions/chords/lyrics
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json

# Backup DB au demarrage
from db_backup import backup_database
backup_database()

# Ajouter le répertoire backend au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app, db
from models.song import Song
from models.book import Book
from models.book_song import BookSong


class MusicBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Book Generator")
        self.root.geometry("1200x800")

        # Initialiser la base de données
        with app.app_context():
            db.create_all()

        # Variables
        self.current_book = None
        self.selected_songs = []

        # Créer l'interface
        self.create_widgets()

        # Charger les données initiales
        self.refresh_catalog()

    def create_widgets(self):
        """Créer l'interface principale"""
        # Notebook (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Onglet 1: Catalogue
        self.create_catalog_tab()

        # Onglet 2: Book Builder
        self.create_book_builder_tab()

        # Onglet 3: Import
        self.create_import_tab()

    def create_catalog_tab(self):
        """Onglet gestion du catalogue"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📚 Catalogue")

        # Frame filtres
        filter_frame = ttk.LabelFrame(tab, text="Filtres", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        # Recherche
        ttk.Label(filter_frame, text="Recherche:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_catalog())
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).grid(row=0, column=1, padx=5)

        # Filtre instrument
        ttk.Label(filter_frame, text="Instrument:").grid(row=0, column=2, padx=5)
        self.instrument_filter = tk.StringVar(value="")
        instrument_combo = ttk.Combobox(filter_frame, textvariable=self.instrument_filter,
                                       values=["", "guitar", "bass", "violin"], state="readonly", width=15)
        instrument_combo.grid(row=0, column=3, padx=5)
        instrument_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_catalog())

        # Filtre difficulté
        ttk.Label(filter_frame, text="Difficulté:").grid(row=0, column=4, padx=5)
        self.difficulty_filter = tk.StringVar(value="")
        difficulty_combo = ttk.Combobox(filter_frame, textvariable=self.difficulty_filter,
                                       values=["", "easy", "medium", "advanced"], state="readonly", width=15)
        difficulty_combo.grid(row=0, column=5, padx=5)
        difficulty_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_catalog())

        # Boutons actions
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="➕ Ajouter un morceau",
                  command=self.add_song).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Éditer",
                  command=self.edit_song).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Supprimer",
                  command=self.delete_song).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Actualiser",
                  command=self.refresh_catalog).pack(side=tk.LEFT, padx=5)

        # Liste des morceaux (Treeview)
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Treeview
        columns = ("artist", "instruments", "difficulty", "key", "pages")
        self.catalog_tree = ttk.Treeview(list_frame, columns=columns,
                                         yscrollcommand=scrollbar.set, selectmode='browse')
        self.catalog_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.catalog_tree.yview)

        # Colonnes
        self.catalog_tree.heading("#0", text="Titre")
        self.catalog_tree.heading("artist", text="Artiste")
        self.catalog_tree.heading("instruments", text="Instruments")
        self.catalog_tree.heading("difficulty", text="Difficulté")
        self.catalog_tree.heading("key", text="Tonalité")
        self.catalog_tree.heading("pages", text="Pages")

        self.catalog_tree.column("#0", width=250)
        self.catalog_tree.column("artist", width=200)
        self.catalog_tree.column("instruments", width=200)
        self.catalog_tree.column("difficulty", width=100)
        self.catalog_tree.column("key", width=80)
        self.catalog_tree.column("pages", width=80)

        # Double-clic pour éditer
        self.catalog_tree.bind('<Double-1>', lambda e: self.edit_song())

    def create_book_builder_tab(self):
        """Onglet construction de books"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📖 Book Builder")

        # Frame du haut : configuration du book
        config_frame = ttk.LabelFrame(tab, text="Configuration du Book", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        # Titre du book
        ttk.Label(config_frame, text="Titre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.book_title_var = tk.StringVar(value="Music Book - Guitare")
        ttk.Entry(config_frame, textvariable=self.book_title_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        # Instrument
        ttk.Label(config_frame, text="Instrument:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.book_instrument_var = tk.StringVar(value="guitar")
        ttk.Combobox(config_frame, textvariable=self.book_instrument_var,
                    values=["guitar", "bass", "violin"], state="readonly", width=15).grid(row=0, column=3, padx=5, pady=5)

        # Options
        self.include_cover_var = tk.BooleanVar(value=True)
        self.include_toc_var = tk.BooleanVar(value=True)
        self.include_index_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(config_frame, text="Page de garde", variable=self.include_cover_var).grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Checkbutton(config_frame, text="Table des matières", variable=self.include_toc_var).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Checkbutton(config_frame, text="Index alphabétique", variable=self.include_index_var).grid(row=1, column=2, sticky=tk.W, padx=5)

        # Boutons
        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)

        ttk.Button(btn_frame, text="💾 Sauvegarder Book",
                  command=self.save_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Générer PDF (3 versions)",
                  command=self.generate_books).pack(side=tk.LEFT, padx=5)

        # Séparateur horizontal
        ttk.Separator(tab, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)

        # Frame du milieu : panneaux gauche/droite
        panes = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Panneau gauche : morceaux disponibles
        left_frame = ttk.LabelFrame(panes, text="Morceaux disponibles", padding=10)
        panes.add(left_frame, weight=1)

        # Liste morceaux disponibles
        scrollbar_left = ttk.Scrollbar(left_frame)
        scrollbar_left.pack(side=tk.RIGHT, fill=tk.Y)

        self.available_tree = ttk.Treeview(left_frame, columns=("artist",),
                                          yscrollcommand=scrollbar_left.set, selectmode='extended')
        self.available_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar_left.config(command=self.available_tree.yview)

        self.available_tree.heading("#0", text="Titre")
        self.available_tree.heading("artist", text="Artiste")
        self.available_tree.column("#0", width=200)
        self.available_tree.column("artist", width=150)

        # Bouton ajouter
        ttk.Button(left_frame, text="➡️ Ajouter au book",
                  command=self.add_to_book).pack(pady=5)

        # Panneau droit : morceaux du book
        right_frame = ttk.LabelFrame(panes, text="Morceaux du book", padding=10)
        panes.add(right_frame, weight=1)

        # Liste morceaux du book
        scrollbar_right = ttk.Scrollbar(right_frame)
        scrollbar_right.pack(side=tk.RIGHT, fill=tk.Y)

        self.book_tree = ttk.Treeview(right_frame, columns=("artist", "pages"),
                                     yscrollcommand=scrollbar_right.set, selectmode='browse')
        self.book_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar_right.config(command=self.book_tree.yview)

        self.book_tree.heading("#0", text="Titre")
        self.book_tree.heading("artist", text="Artiste")
        self.book_tree.heading("pages", text="Pages")
        self.book_tree.column("#0", width=200)
        self.book_tree.column("artist", width=150)
        self.book_tree.column("pages", width=80)

        # Boutons
        btn_frame_right = ttk.Frame(right_frame)
        btn_frame_right.pack(pady=5)

        ttk.Button(btn_frame_right, text="⬆️ Monter",
                  command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame_right, text="⬇️ Descendre",
                  command=self.move_down).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame_right, text="🗑️ Retirer",
                  command=self.remove_from_book).pack(side=tk.LEFT, padx=2)

        # Label info
        self.book_info_label = ttk.Label(right_frame, text="Book vide", font=('Arial', 10, 'italic'))
        self.book_info_label.pack(pady=5)

        # Charger morceaux disponibles
        self.refresh_available_songs()

    def create_import_tab(self):
        """Onglet import de PDF"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📥 Import PDF")

        # Frame principal
        frame = ttk.LabelFrame(tab, text="Importer des fichiers PDF", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Instructions
        ttk.Label(frame, text="Sélectionnez des fichiers PDF de partitions/chords/lyrics",
                 font=('Arial', 12)).pack(pady=10)

        # Bouton sélection
        ttk.Button(frame, text="📁 Sélectionner des fichiers PDF",
                  command=self.import_pdfs, style='Large.TButton').pack(pady=20)

        # Informations
        info_text = """
        Instructions :
        1. Cliquez sur "Sélectionner des fichiers PDF"
        2. Choisissez un ou plusieurs fichiers PDF
        3. Renseignez les métadonnées pour chaque fichier
        4. Les fichiers seront ajoutés au catalogue

        Formats acceptés : PDF uniquement
        Taille max : 50 MB par fichier
        """
        ttk.Label(frame, text=info_text, justify=tk.LEFT,
                 font=('Arial', 10)).pack(pady=10)

    # ===== MÉTHODES CATALOGUE =====

    def refresh_catalog(self):
        """Actualiser la liste du catalogue"""
        # Vider la liste
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        # Requête avec filtres
        with app.app_context():
            query = Song.query

            # Filtre recherche
            search = self.search_var.get().strip()
            if search:
                query = query.filter(
                    db.or_(
                        Song.title.ilike(f'%{search}%'),
                        Song.artist.ilike(f'%{search}%')
                    )
                )

            # Filtre instrument
            instrument = self.instrument_filter.get()
            if instrument:
                query = query.filter(Song.instruments.contains(f'"{instrument}"'))

            # Filtre difficulté
            difficulty = self.difficulty_filter.get()
            if difficulty:
                query = query.filter(Song.difficulty == difficulty)

            songs = query.order_by(Song.title).all()

            # Ajouter à la liste
            for song in songs:
                instruments = ', '.join(json.loads(song.instruments) if song.instruments else [])
                self.catalog_tree.insert('', tk.END, text=song.title, iid=str(song.id),
                                        values=(song.artist or '', instruments,
                                               song.difficulty or '', song.key or '',
                                               song.pages or ''))

    def add_song(self):
        """Ajouter un morceau"""
        dialog = SongDialog(self.root, "Ajouter un morceau")
        if dialog.result:
            with app.app_context():
                song = Song.from_dict(dialog.result)
                db.session.add(song)
                db.session.commit()

            messagebox.showinfo("Succès", "Morceau ajouté avec succès")
            self.refresh_catalog()
            self.refresh_available_songs()

    def edit_song(self):
        """Éditer un morceau"""
        selection = self.catalog_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un morceau à éditer")
            return

        song_id = int(selection[0])

        with app.app_context():
            song = Song.query.get(song_id)
            if not song:
                messagebox.showerror("Erreur", "Morceau introuvable")
                return

            song_data = song.to_dict()

        dialog = SongDialog(self.root, "Éditer le morceau", song_data)
        if dialog.result:
            with app.app_context():
                song = Song.query.get(song_id)

                # Mise à jour
                song.title = dialog.result['title']
                song.artist = dialog.result.get('artist')
                song.key = dialog.result.get('key')
                song.tempo = dialog.result.get('tempo')
                song.genre = dialog.result.get('genre')
                song.difficulty = dialog.result.get('difficulty')
                song.instruments = json.dumps(dialog.result.get('instruments', []))
                song.pages = dialog.result.get('pages')
                song.notes = dialog.result.get('notes')

                db.session.commit()

            messagebox.showinfo("Succès", "Morceau modifié avec succès")
            self.refresh_catalog()
            self.refresh_available_songs()

    def delete_song(self):
        """Supprimer un morceau"""
        selection = self.catalog_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un morceau à supprimer")
            return

        if not messagebox.askyesno("Confirmation",
                                   "Êtes-vous sûr de vouloir supprimer ce morceau ?"):
            return

        song_id = int(selection[0])

        with app.app_context():
            song = Song.query.get(song_id)
            if song:
                db.session.delete(song)
                db.session.commit()

        messagebox.showinfo("Succès", "Morceau supprimé")
        self.refresh_catalog()
        self.refresh_available_songs()

    # ===== MÉTHODES BOOK BUILDER =====

    def refresh_available_songs(self):
        """Actualiser la liste des morceaux disponibles"""
        # Vider la liste
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)

        with app.app_context():
            songs = Song.query.order_by(Song.title).all()

            for song in songs:
                self.available_tree.insert('', tk.END, text=song.title, iid=str(song.id),
                                          values=(song.artist or '',))

    def add_to_book(self):
        """Ajouter morceaux sélectionnés au book"""
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez au moins un morceau")
            return

        for song_id in selection:
            song_id = int(song_id)

            # Vérifier si déjà dans le book
            if song_id in self.selected_songs:
                continue

            with app.app_context():
                song = Song.query.get(song_id)
                if song:
                    self.selected_songs.append(song_id)
                    self.book_tree.insert('', tk.END, text=song.title, iid=str(song.id),
                                         values=(song.artist or '', song.pages or ''))

        self.update_book_info()

    def remove_from_book(self):
        """Retirer un morceau du book"""
        selection = self.book_tree.selection()
        if not selection:
            return

        song_id = int(selection[0])
        self.selected_songs.remove(song_id)
        self.book_tree.delete(selection[0])
        self.update_book_info()

    def move_up(self):
        """Déplacer un morceau vers le haut"""
        selection = self.book_tree.selection()
        if not selection:
            return

        item = selection[0]
        index = self.book_tree.index(item)

        if index > 0:
            self.book_tree.move(item, '', index - 1)

            # Mettre à jour selected_songs
            song_id = int(item)
            self.selected_songs.remove(song_id)
            self.selected_songs.insert(index - 1, song_id)

    def move_down(self):
        """Déplacer un morceau vers le bas"""
        selection = self.book_tree.selection()
        if not selection:
            return

        item = selection[0]
        index = self.book_tree.index(item)

        if index < len(self.book_tree.get_children()) - 1:
            self.book_tree.move(item, '', index + 1)

            # Mettre à jour selected_songs
            song_id = int(item)
            self.selected_songs.remove(song_id)
            self.selected_songs.insert(index + 1, song_id)

    def update_book_info(self):
        """Mettre à jour les infos du book"""
        if not self.selected_songs:
            self.book_info_label.config(text="Book vide")
            return

        total_pages = 0
        with app.app_context():
            for song_id in self.selected_songs:
                song = Song.query.get(song_id)
                if song and song.pages:
                    total_pages += song.pages

        # Ajouter pages système
        if self.include_cover_var.get():
            total_pages += 1
        if self.include_toc_var.get():
            total_pages += 2
        if self.include_index_var.get():
            total_pages += 1

        self.book_info_label.config(
            text=f"{len(self.selected_songs)} morceaux • ~{total_pages} pages"
        )

    def save_book(self):
        """Sauvegarder le book dans la base de données"""
        if not self.selected_songs:
            messagebox.showwarning("Attention", "Le book est vide")
            return

        with app.app_context():
            book = Book(
                title=self.book_title_var.get(),
                instrument=self.book_instrument_var.get(),
                include_cover=self.include_cover_var.get(),
                include_toc=self.include_toc_var.get(),
                include_index=self.include_index_var.get()
            )
            db.session.add(book)
            db.session.flush()  # Pour obtenir l'ID

            # Ajouter les morceaux
            for position, song_id in enumerate(self.selected_songs, start=1):
                book_song = BookSong(
                    book_id=book.id,
                    song_id=song_id,
                    position=position
                )
                db.session.add(book_song)

            db.session.commit()
            self.current_book = book.id

        messagebox.showinfo("Succès", f"Book sauvegardé (ID: {self.current_book})")

    def generate_books(self):
        """Générer le PDF du book"""
        if not self.selected_songs:
            messagebox.showwarning("Attention", "Le book est vide")
            return

        # Import du générateur
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'services'))
        from pdf_generator import MusicBookGenerator

        try:
            # Générer le PDF
            generator = MusicBookGenerator()
            output_path = generator.generate_from_song_ids(
                song_ids=self.selected_songs,
                title=self.book_title_var.get(),
                instrument=self.book_instrument_var.get(),
                include_cover=self.include_cover_var.get(),
                include_toc=self.include_toc_var.get(),
                include_index=self.include_index_var.get()
            )

            # Afficher le résultat
            messagebox.showinfo(
                "Succès",
                f"PDF généré avec succès!\n\n{output_path}"
            )

            # Proposer d'ouvrir le fichier
            if messagebox.askyesno("Ouvrir", "Voulez-vous ouvrir le PDF ?"):
                import subprocess
                subprocess.run(['xdg-open', output_path], check=False)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération:\n{str(e)}")

    # ===== MÉTHODES IMPORT =====

    def import_pdfs(self):
        """Importer des fichiers PDF"""
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )

        if not files:
            return

        for file_path in files:
            # Extraire le nom du fichier comme titre par défaut
            title = Path(file_path).stem

            # Dialogue pour métadonnées
            dialog = SongDialog(self.root, f"Métadonnées - {title}",
                               {'title': title, 'pdf_path': file_path})

            if dialog.result:
                with app.app_context():
                    song = Song.from_dict(dialog.result)
                    db.session.add(song)
                    db.session.commit()

        messagebox.showinfo("Succès", f"{len(files)} fichier(s) importé(s)")
        self.refresh_catalog()
        self.refresh_available_songs()


class SongDialog:
    """Dialogue pour ajouter/éditer un morceau"""

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

        # Titre
        ttk.Label(frame, text="Titre *").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_var = tk.StringVar(value=song_data.get('title', '') if song_data else '')
        ttk.Entry(frame, textvariable=self.title_var, width=40).grid(row=0, column=1, pady=5)

        # Artiste
        ttk.Label(frame, text="Artiste").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.artist_var = tk.StringVar(value=song_data.get('artist', '') if song_data else '')
        ttk.Entry(frame, textvariable=self.artist_var, width=40).grid(row=1, column=1, pady=5)

        # Tonalité
        ttk.Label(frame, text="Tonalité").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.key_var = tk.StringVar(value=song_data.get('key', '') if song_data else '')
        ttk.Entry(frame, textvariable=self.key_var, width=40).grid(row=2, column=1, pady=5)

        # Tempo
        ttk.Label(frame, text="Tempo (BPM)").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.tempo_var = tk.StringVar(value=str(song_data.get('tempo', '')) if song_data and song_data.get('tempo') else '')
        ttk.Entry(frame, textvariable=self.tempo_var, width=40).grid(row=3, column=1, pady=5)

        # Genre
        ttk.Label(frame, text="Genre").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.genre_var = tk.StringVar(value=song_data.get('genre', '') if song_data else '')
        ttk.Entry(frame, textvariable=self.genre_var, width=40).grid(row=4, column=1, pady=5)

        # Difficulté
        ttk.Label(frame, text="Difficulté").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.difficulty_var = tk.StringVar(value=song_data.get('difficulty', '') if song_data else '')
        ttk.Combobox(frame, textvariable=self.difficulty_var,
                    values=["", "easy", "medium", "advanced"], width=37).grid(row=5, column=1, pady=5)

        # Instruments (checkboxes)
        ttk.Label(frame, text="Instruments").grid(row=6, column=0, sticky=tk.W, pady=5)
        instruments_frame = ttk.Frame(frame)
        instruments_frame.grid(row=6, column=1, sticky=tk.W, pady=5)

        self.guitar_var = tk.BooleanVar(value='guitar' in song_data.get('instruments', []) if song_data else False)
        self.bass_var = tk.BooleanVar(value='bass' in song_data.get('instruments', []) if song_data else False)
        self.violin_var = tk.BooleanVar(value='violin' in song_data.get('instruments', []) if song_data else False)

        ttk.Checkbutton(instruments_frame, text="Guitare", variable=self.guitar_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(instruments_frame, text="Basse", variable=self.bass_var).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(instruments_frame, text="Violon", variable=self.violin_var).pack(side=tk.LEFT, padx=5)

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

        # PDF path (caché pour import)
        self.pdf_path = song_data.get('pdf_path', '') if song_data else ''

        # Boutons
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="💾 Enregistrer", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Annuler", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Attendre la fermeture
        parent.wait_window(self.dialog)

    def save(self):
        """Sauvegarder les données"""
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
        pdf_path = self.pdf_path or f'/data/projects/music-book/data/pdfs/placeholder_{title.replace(" ", "_")}.pdf'

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


def main():
    root = tk.Tk()

    # Style
    style = ttk.Style()
    style.theme_use('clam')

    # Bouton large pour import
    style.configure('Large.TButton', font=('Arial', 12), padding=10)

    app = MusicBookGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
