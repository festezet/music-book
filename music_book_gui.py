#!/usr/bin/env python3
"""
Music Book Generator - Interface GUI Tkinter
Application desktop pour créer des livres de partitions/chords/lyrics
"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Backup DB au demarrage
from db_backup import backup_database
backup_database()

from music_book_operations import (
    init_database, query_catalog_songs, get_song_for_edit,
    update_song_from_dict, create_song, delete_song_by_id,
    get_available_songs, get_song_info, calculate_book_pages,
    save_book_to_db, generate_pdf
)


class MusicBookGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Book Generator")
        self.root.geometry("1200x800")

        init_database()

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

        self._create_catalog_filters(tab)
        self._create_catalog_buttons(tab)
        self._create_catalog_treeview(tab)

    def _create_catalog_filters(self, tab):
        """Create filter section for the catalog tab."""
        filter_frame = ttk.LabelFrame(tab, text="Filtres", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(filter_frame, text="Recherche:").grid(row=0, column=0, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.refresh_catalog())
        ttk.Entry(filter_frame, textvariable=self.search_var, width=30).grid(row=0, column=1, padx=5)

        ttk.Label(filter_frame, text="Instrument:").grid(row=0, column=2, padx=5)
        self.instrument_filter = tk.StringVar(value="")
        instrument_combo = ttk.Combobox(filter_frame, textvariable=self.instrument_filter,
                                       values=["", "guitar", "bass", "violin"], state="readonly", width=15)
        instrument_combo.grid(row=0, column=3, padx=5)
        instrument_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_catalog())

        ttk.Label(filter_frame, text="Difficulté:").grid(row=0, column=4, padx=5)
        self.difficulty_filter = tk.StringVar(value="")
        difficulty_combo = ttk.Combobox(filter_frame, textvariable=self.difficulty_filter,
                                       values=["", "easy", "medium", "advanced"], state="readonly", width=15)
        difficulty_combo.grid(row=0, column=5, padx=5)
        difficulty_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_catalog())

    def _create_catalog_buttons(self, tab):
        """Create action buttons for the catalog tab."""
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

    def _create_catalog_treeview(self, tab):
        """Create the treeview for catalog song listing."""
        list_frame = ttk.Frame(tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("artist", "instruments", "difficulty", "key", "pages")
        self.catalog_tree = ttk.Treeview(list_frame, columns=columns,
                                         yscrollcommand=scrollbar.set, selectmode='browse')
        self.catalog_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.catalog_tree.yview)

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

        self.catalog_tree.bind('<Double-1>', lambda e: self.edit_song())

    def create_book_builder_tab(self):
        """Onglet construction de books"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📖 Book Builder")

        self._create_book_config_frame(tab)
        ttk.Separator(tab, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=10, pady=10)
        self._create_book_panes(tab)
        self.refresh_available_songs()

    def _create_book_config_frame(self, tab):
        """Create book configuration section with title, instrument and options."""
        config_frame = ttk.LabelFrame(tab, text="Configuration du Book", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(config_frame, text="Titre:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.book_title_var = tk.StringVar(value="Music Book - Guitare")
        ttk.Entry(config_frame, textvariable=self.book_title_var, width=40).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="Instrument:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.book_instrument_var = tk.StringVar(value="guitar")
        ttk.Combobox(config_frame, textvariable=self.book_instrument_var,
                    values=["guitar", "bass", "violin"], state="readonly", width=15).grid(row=0, column=3, padx=5, pady=5)

        self.include_cover_var = tk.BooleanVar(value=True)
        self.include_toc_var = tk.BooleanVar(value=True)
        self.include_index_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(config_frame, text="Page de garde", variable=self.include_cover_var).grid(row=1, column=0, sticky=tk.W, padx=5)
        ttk.Checkbutton(config_frame, text="Table des matières", variable=self.include_toc_var).grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Checkbutton(config_frame, text="Index alphabétique", variable=self.include_index_var).grid(row=1, column=2, sticky=tk.W, padx=5)

        btn_frame = ttk.Frame(config_frame)
        btn_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(btn_frame, text="💾 Sauvegarder Book",
                  command=self.save_book).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📄 Générer PDF (3 versions)",
                  command=self.generate_books).pack(side=tk.LEFT, padx=5)

    def _create_book_panes(self, tab):
        """Create left/right panes for available songs and book songs."""
        panes = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        panes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._create_available_songs_pane(panes)
        self._create_book_songs_pane(panes)

    def _create_available_songs_pane(self, panes):
        """Create left pane with available songs list."""
        left_frame = ttk.LabelFrame(panes, text="Morceaux disponibles", padding=10)
        panes.add(left_frame, weight=1)

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

        ttk.Button(left_frame, text="➡️ Ajouter au book",
                  command=self.add_to_book).pack(pady=5)

    def _create_book_songs_pane(self, panes):
        """Create right pane with book songs list and controls."""
        right_frame = ttk.LabelFrame(panes, text="Morceaux du book", padding=10)
        panes.add(right_frame, weight=1)

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

        btn_frame_right = ttk.Frame(right_frame)
        btn_frame_right.pack(pady=5)
        ttk.Button(btn_frame_right, text="⬆️ Monter",
                  command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame_right, text="⬇️ Descendre",
                  command=self.move_down).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame_right, text="🗑️ Retirer",
                  command=self.remove_from_book).pack(side=tk.LEFT, padx=2)

        self.book_info_label = ttk.Label(right_frame, text="Book vide", font=('Arial', 10, 'italic'))
        self.book_info_label.pack(pady=5)

    def create_import_tab(self):
        """Onglet import de PDF"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📥 Import PDF")

        frame = ttk.LabelFrame(tab, text="Importer des fichiers PDF", padding=20)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Sélectionnez des fichiers PDF de partitions/chords/lyrics",
                 font=('Arial', 12)).pack(pady=10)

        ttk.Button(frame, text="📁 Sélectionner des fichiers PDF",
                  command=self.import_pdfs, style='Large.TButton').pack(pady=20)

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

    # ===== METHODES CATALOGUE =====

    def refresh_catalog(self):
        """Actualiser la liste du catalogue"""
        for item in self.catalog_tree.get_children():
            self.catalog_tree.delete(item)

        songs = query_catalog_songs(
            search=self.search_var.get().strip(),
            instrument=self.instrument_filter.get(),
            difficulty=self.difficulty_filter.get()
        )
        for song in songs:
            self.catalog_tree.insert('', tk.END, text=song['title'], iid=str(song['id']),
                                    values=(song['artist'], song['instruments'],
                                           song['difficulty'], song['key'],
                                           song['pages']))

    def add_song(self):
        """Ajouter un morceau"""
        dialog = SongDialog(self.root, "Ajouter un morceau")
        if dialog.result:
            create_song(dialog.result)
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
        song_data = get_song_for_edit(song_id)
        if not song_data:
            messagebox.showerror("Erreur", "Morceau introuvable")
            return

        dialog = SongDialog(self.root, "Éditer le morceau", song_data)
        if dialog.result:
            update_song_from_dict(song_id, dialog.result)
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

        delete_song_by_id(int(selection[0]))
        messagebox.showinfo("Succès", "Morceau supprimé")
        self.refresh_catalog()
        self.refresh_available_songs()

    # ===== METHODES BOOK BUILDER =====

    def refresh_available_songs(self):
        """Actualiser la liste des morceaux disponibles"""
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)

        for song_id, title, artist in get_available_songs():
            self.available_tree.insert('', tk.END, text=title, iid=str(song_id),
                                      values=(artist,))

    def add_to_book(self):
        """Ajouter morceaux sélectionnés au book"""
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez au moins un morceau")
            return

        for item_id in selection:
            song_id = int(item_id)
            if song_id in self.selected_songs:
                continue
            info = get_song_info(song_id)
            if info:
                self.selected_songs.append(song_id)
                self.book_tree.insert('', tk.END, text=info[0], iid=str(song_id),
                                     values=(info[1], info[2]))
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
            song_id = int(item)
            self.selected_songs.remove(song_id)
            self.selected_songs.insert(index + 1, song_id)

    def update_book_info(self):
        """Mettre à jour les infos du book"""
        if not self.selected_songs:
            self.book_info_label.config(text="Book vide")
            return

        song_count, total_pages = calculate_book_pages(
            self.selected_songs,
            self.include_cover_var.get(),
            self.include_toc_var.get(),
            self.include_index_var.get()
        )
        self.book_info_label.config(
            text=f"{song_count} morceaux • ~{total_pages} pages"
        )

    def save_book(self):
        """Sauvegarder le book dans la base de données"""
        if not self.selected_songs:
            messagebox.showwarning("Attention", "Le book est vide")
            return

        book_options = {
            'include_cover': self.include_cover_var.get(),
            'include_toc': self.include_toc_var.get(),
            'include_index': self.include_index_var.get(),
        }
        self.current_book = save_book_to_db(
            self.book_title_var.get(),
            self.book_instrument_var.get(),
            book_options,
            self.selected_songs
        )
        messagebox.showinfo("Succès", f"Book sauvegardé (ID: {self.current_book})")

    def generate_books(self):
        """Générer le PDF du book"""
        if not self.selected_songs:
            messagebox.showwarning("Attention", "Le book est vide")
            return

        try:
            gen_options = {
                'include_cover': self.include_cover_var.get(),
                'include_toc': self.include_toc_var.get(),
                'include_index': self.include_index_var.get(),
            }
            output_path = generate_pdf(
                self.selected_songs,
                self.book_title_var.get(),
                self.book_instrument_var.get(),
                gen_options
            )
            messagebox.showinfo("Succès", f"PDF généré avec succès!\n\n{output_path}")
            if messagebox.askyesno("Ouvrir", "Voulez-vous ouvrir le PDF ?"):
                import subprocess
                subprocess.run(['xdg-open', output_path], check=False)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération:\n{str(e)}")

    # ===== METHODES IMPORT =====

    def import_pdfs(self):
        """Importer des fichiers PDF"""
        files = filedialog.askopenfilenames(
            title="Sélectionner des fichiers PDF",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not files:
            return

        for file_path in files:
            title = Path(file_path).stem
            dialog = SongDialog(self.root, f"Métadonnées - {title}",
                               {'title': title, 'pdf_path': file_path})
            if dialog.result:
                create_song(dialog.result)

        messagebox.showinfo("Succès", f"{len(files)} fichier(s) importé(s)")
        self.refresh_catalog()
        self.refresh_available_songs()


# SongDialog extracted to song_dialog.py for modularity
from song_dialog import SongDialog  # noqa: E402


def main():
    root = tk.Tk()

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Large.TButton', font=('Arial', 12), padding=10)

    app = MusicBookGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
