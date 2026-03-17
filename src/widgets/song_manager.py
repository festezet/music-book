"""
Song Manager - Gestion de la bibliotheque de morceaux
Permet d'ajouter, editer et supprimer des morceaux
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Optional, Dict, Any, List
import os

from . import song_db
from .song_manager_list_display import create_song_item, open_pdf, open_folder


class SongManagerDialog(ctk.CTkToplevel):
    """Fenetre de gestion de la bibliotheque de morceaux"""

    GENRE_OPTIONS = [
        "Rock", "Pop", "Chanson Francaise", "Blues", "Jazz", "Folk",
        "Country", "Metal", "Classique", "Reggae", "Funk", "Soul",
        "Variete", "Autre"
    ]

    SOURCE_OPTIONS = [
        ("Ultimate Guitar", "ultimate_guitar"),
        ("Songsterr", "songsterr"),
        ("Boite a chansons", "boite_chansons"),
        ("Autre", "other")
    ]

    INSTRUMENT_OPTIONS = [
        ("Guitare", "guitar"), ("Basse", "bass"), ("Violon", "violin"),
        ("Piano", "piano"), ("Ukulele", "ukulele")
    ]

    TYPE_OPTIONS = [
        ("Accords", "chords"), ("Tablature", "tab"), ("Partition", "sheet")
    ]

    def __init__(self, parent, on_close: Callable = None):
        super().__init__(parent)
        self.on_close = on_close
        self.selected_song_id: Optional[int] = None
        self.all_songs: List[Dict[str, Any]] = []

        self.title("Gestion de la Bibliotheque")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        self.transient(parent)

        self._create_widgets()
        self._load_songs()
        self.after(100, self._make_modal)

    def _make_modal(self):
        """Rendre la fenetre modale apres affichage"""
        try:
            self.grab_set()
        except Exception:
            pass

    # -----------------------------------------------------------------
    # LAYOUT
    # -----------------------------------------------------------------

    def _create_widgets(self):
        """Creer l'interface"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        self._create_header()
        self._create_list_panel()
        self._create_form_panel()

    def _create_header(self):
        """Creer le header avec titre et bouton fermer."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header, text="Gestion de la Bibliotheque",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header, text="Fermer", width=100,
            fg_color="#6b7280", hover_color="#4b5563", command=self._close
        ).pack(side="right")

    def _create_list_panel(self):
        """Creer le panneau liste des morceaux (gauche)."""
        list_frame = ctk.CTkFrame(self, corner_radius=10)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        list_frame.grid_rowconfigure(2, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            list_header, text="Morceaux",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        self.song_count_label = ctk.CTkLabel(
            list_header, text="(0)", font=ctk.CTkFont(size=12),
            text_color=("#6b7280", "#9ca3af")
        )
        self.song_count_label.pack(side="left", padx=5)

        ctk.CTkButton(
            list_header, text="Importer PDFs", width=110,
            fg_color="#16a34a", hover_color="#15803d", command=self._import_pdfs
        ).pack(side="right")

        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *args: self._update_song_list())
        ctk.CTkEntry(
            search_frame, textvariable=self.search_var,
            placeholder_text="Rechercher...", width=200
        ).pack(fill="x")

        self.song_list = ctk.CTkScrollableFrame(list_frame, width=350)
        self.song_list.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.song_list.grid_columnconfigure(0, weight=1)

    def _create_form_panel(self):
        """Creer le panneau formulaire d'edition (droite)."""
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        form_frame.grid_columnconfigure(1, weight=1)

        self.form_title = ctk.CTkLabel(
            form_frame, text="Nouveau morceau",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 20))

        row = self._create_form_fields(form_frame, start_row=1)
        self._create_form_buttons(form_frame, row)

    def _create_form_fields(self, form_frame, start_row: int) -> int:
        """Creer les champs du formulaire. Retourne le prochain row."""
        row = start_row
        row = self._create_text_fields(form_frame, row)
        row = self._create_option_fields(form_frame, row)
        row = self._create_instrument_field(form_frame, row)
        row = self._create_pdf_field(form_frame, row)
        row = self._create_extra_fields(form_frame, row)
        return row

    def _create_text_fields(self, form_frame, row: int) -> int:
        """Create title and artist text entry fields."""
        ctk.CTkLabel(form_frame, text="Titre *").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.title_entry = ctk.CTkEntry(form_frame, width=300)
        self.title_entry.grid(row=row, column=1, sticky="ew", padx=20, pady=5)
        row += 1

        ctk.CTkLabel(form_frame, text="Artiste").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.artist_entry = ctk.CTkEntry(form_frame, width=300)
        self.artist_entry.grid(row=row, column=1, sticky="ew", padx=20, pady=5)
        row += 1
        return row

    def _create_option_fields(self, form_frame, row: int) -> int:
        """Create genre, source and type option menu fields."""
        ctk.CTkLabel(form_frame, text="Genre").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.genre_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(
            form_frame, values=self.GENRE_OPTIONS, variable=self.genre_var, width=200
        ).grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        ctk.CTkLabel(form_frame, text="Source").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.source_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(
            form_frame, values=[s[0] for s in self.SOURCE_OPTIONS],
            variable=self.source_var, width=200
        ).grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        ctk.CTkLabel(form_frame, text="Type").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.type_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(
            form_frame, values=[t[0] for t in self.TYPE_OPTIONS],
            variable=self.type_var, width=200
        ).grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1
        return row

    def _create_instrument_field(self, form_frame, row: int) -> int:
        """Create instruments checkbox field."""
        ctk.CTkLabel(form_frame, text="Instruments").grid(row=row, column=0, sticky="nw", padx=20, pady=5)
        inst_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        inst_frame.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        self.instrument_vars = {}
        for i, (label, value) in enumerate(self.INSTRUMENT_OPTIONS):
            var = ctk.BooleanVar(value=False)
            self.instrument_vars[value] = var
            ctk.CTkCheckBox(inst_frame, text=label, variable=var).grid(row=0, column=i, padx=5)
        row += 1
        return row

    def _create_pdf_field(self, form_frame, row: int) -> int:
        """Create PDF file browser field."""
        ctk.CTkLabel(form_frame, text="Fichier PDF *").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        pdf_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        pdf_frame.grid(row=row, column=1, sticky="ew", padx=20, pady=5)
        pdf_frame.grid_columnconfigure(0, weight=1)
        self.pdf_path_var = ctk.StringVar()
        ctk.CTkEntry(pdf_frame, textvariable=self.pdf_path_var, state="readonly").grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(pdf_frame, text="Parcourir...", width=100, command=self._browse_pdf).grid(row=0, column=1, padx=(10, 0))
        row += 1
        return row

    def _create_extra_fields(self, form_frame, row: int) -> int:
        """Create pages, key and notes fields."""
        ctk.CTkLabel(form_frame, text="Nombre de pages").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.pages_entry = ctk.CTkEntry(form_frame, width=80)
        self.pages_entry.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        ctk.CTkLabel(form_frame, text="Tonalite").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.key_entry = ctk.CTkEntry(form_frame, width=80, placeholder_text="ex: Am, G, D")
        self.key_entry.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        ctk.CTkLabel(form_frame, text="Notes").grid(row=row, column=0, sticky="nw", padx=20, pady=5)
        self.notes_entry = ctk.CTkTextbox(form_frame, height=60)
        self.notes_entry.grid(row=row, column=1, sticky="ew", padx=20, pady=5)
        row += 1

        return row

    def _create_form_buttons(self, form_frame, row: int):
        """Creer les boutons d'action du formulaire."""
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        self.save_btn = ctk.CTkButton(
            btn_frame, text="Enregistrer", width=120,
            fg_color="#16a34a", hover_color="#15803d", command=self._save_song
        )
        self.save_btn.pack(side="left", padx=10)

        self.delete_btn = ctk.CTkButton(
            btn_frame, text="Supprimer", width=120,
            fg_color="#ef4444", hover_color="#dc2626", command=self._delete_song
        )
        self.delete_btn.pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame, text="Annuler", width=120,
            fg_color="#6b7280", hover_color="#4b5563", command=self._clear_form
        ).pack(side="left", padx=10)

    # -----------------------------------------------------------------
    # SONG LIST
    # -----------------------------------------------------------------

    def _load_songs(self):
        """Charger les morceaux depuis la base"""
        try:
            self.all_songs = song_db.load_all_songs()
            print(f"[SongManager] Charge {len(self.all_songs)} morceaux")
        except Exception as e:
            print(f"[SongManager] Erreur chargement morceaux: {e}")
            self.all_songs = []
        self._update_song_list()

    def _update_song_list(self):
        """Mettre a jour l'affichage de la liste"""
        for widget in self.song_list.winfo_children():
            widget.destroy()

        search = self.search_var.get().lower()
        filtered = [
            s for s in self.all_songs
            if not search or search in s['title'].lower()
            or search in (s.get('artist') or '').lower()
        ]
        self.song_count_label.configure(text=f"({len(filtered)})")

        for song in filtered:
            self._create_song_item(song)

    def _create_song_item(self, song: Dict):
        """Creer un element de liste pour un morceau"""
        is_selected = self.selected_song_id == song['id']
        create_song_item(
            self.song_list, song, is_selected,
            self._select_song, self._show_context_menu
        )

    # -----------------------------------------------------------------
    # CONTEXT MENU
    # -----------------------------------------------------------------

    def _show_context_menu(self, event, song: Dict):
        """Afficher le menu contextuel pour un morceau"""
        import tkinter as tk
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Ouvrir le PDF", command=lambda: open_pdf(song))
        menu.add_command(label="Ouvrir le dossier", command=lambda: open_folder(song))
        menu.add_separator()
        menu.add_command(label="Editer", command=lambda: self._select_song(song))
        menu.add_command(label="Supprimer", command=lambda: self._delete_song_direct(song))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    # -----------------------------------------------------------------
    # FORM OPERATIONS
    # -----------------------------------------------------------------

    def _select_song(self, song: Dict):
        """Selectionner un morceau pour edition"""
        self.selected_song_id = song['id']
        self.form_title.configure(text=f"Modifier: {song['title']}")

        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, song.get('title', ''))
        self.artist_entry.delete(0, "end")
        self.artist_entry.insert(0, song.get('artist') or '')
        self.genre_var.set(song.get('genre') or self.GENRE_OPTIONS[0])

        source = song.get('source') or ''
        self.source_var.set(
            next((s[0] for s in self.SOURCE_OPTIONS if s[1] == source), self.SOURCE_OPTIONS[0][0])
        )
        song_type = song.get('type') or ''
        self.type_var.set(
            next((t[0] for t in self.TYPE_OPTIONS if t[1] == song_type), self.TYPE_OPTIONS[0][0])
        )

        for inst, var in self.instrument_vars.items():
            var.set(inst in (song.get('instruments') or []))

        self.pdf_path_var.set(song.get('pdf_path') or '')
        self.pages_entry.delete(0, "end")
        self.pages_entry.insert(0, str(song.get('pages') or 1))
        self.key_entry.delete(0, "end")
        self.key_entry.insert(0, song.get('key') or '')
        self.notes_entry.delete("1.0", "end")
        self.notes_entry.insert("1.0", song.get('notes') or '')
        self.delete_btn.configure(state="normal")
        self._update_song_list()

    def _clear_form(self):
        """Vider le formulaire"""
        self.selected_song_id = None
        self.form_title.configure(text="Nouveau morceau")
        self.title_entry.delete(0, "end")
        self.artist_entry.delete(0, "end")
        self.genre_var.set(self.GENRE_OPTIONS[0])
        self.source_var.set(self.SOURCE_OPTIONS[0][0])
        self.type_var.set(self.TYPE_OPTIONS[0][0])
        for var in self.instrument_vars.values():
            var.set(False)
        self.pdf_path_var.set("")
        self.pages_entry.delete(0, "end")
        self.key_entry.delete(0, "end")
        self.notes_entry.delete("1.0", "end")
        self.delete_btn.configure(state="disabled")

    def _browse_pdf(self):
        """Ouvrir dialogue de selection de fichier PDF"""
        filepath = filedialog.askopenfilename(
            title="Selectionner un fichier PDF",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
            initialdir=os.path.join(os.path.expanduser("~"), "Downloads")
        )
        if not filepath:
            return
        self.pdf_path_var.set(filepath)
        try:
            from PyPDF2 import PdfReader
            pages = len(PdfReader(filepath).pages)
            self.pages_entry.delete(0, "end")
            self.pages_entry.insert(0, str(pages))
        except Exception:
            pass
        if not self.title_entry.get().strip():
            title = os.path.splitext(os.path.basename(filepath))[0]
            self.title_entry.delete(0, "end")
            self.title_entry.insert(0, title)

    def _collect_form_data(self) -> Optional[Dict[str, Any]]:
        """Collecter et valider les donnees du formulaire. None si invalide."""
        title = self.title_entry.get().strip()
        pdf_path = self.pdf_path_var.get().strip()

        if not title:
            messagebox.showerror("Erreur", "Le titre est obligatoire")
            return None
        if not pdf_path:
            messagebox.showerror("Erreur", "Le fichier PDF est obligatoire")
            return None
        if not os.path.exists(pdf_path):
            messagebox.showerror("Erreur", f"Le fichier PDF n'existe pas:\n{pdf_path}")
            return None

        genre = self.genre_var.get()
        source = next((v for l, v in self.SOURCE_OPTIONS if l == self.source_var.get()), None)
        song_type = next((v for l, v in self.TYPE_OPTIONS if l == self.type_var.get()), None)

        try:
            pages = int(self.pages_entry.get()) if self.pages_entry.get() else 1
        except ValueError:
            pages = 1

        return {
            'title': title,
            'artist': self.artist_entry.get().strip() or None,
            'genre': genre if genre != self.GENRE_OPTIONS[0] else None,
            'source': source,
            'type': song_type,
            'instruments': [i for i, v in self.instrument_vars.items() if v.get()],
            'pdf_path': pdf_path,
            'pages': pages,
            'key': self.key_entry.get().strip() or None,
            'notes': self.notes_entry.get("1.0", "end").strip() or None,
        }

    # -----------------------------------------------------------------
    # DB ACTIONS
    # -----------------------------------------------------------------

    def _save_song(self):
        """Enregistrer le morceau (creation ou mise a jour)"""
        data = self._collect_form_data()
        if not data:
            return
        try:
            msg = song_db.save_song(data, self.selected_song_id)
            messagebox.showinfo("Succes", msg)
            self._load_songs()
            self._clear_form()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{e}")

    def _delete_song(self):
        """Supprimer le morceau selectionne"""
        if not self.selected_song_id:
            return
        if not messagebox.askyesno("Confirmation", "Voulez-vous vraiment supprimer ce morceau?"):
            return
        try:
            song_db.delete_song(self.selected_song_id)
            messagebox.showinfo("Succes", "Morceau supprime")
            self._load_songs()
            self._clear_form()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{e}")

    def _delete_song_direct(self, song: Dict):
        """Supprimer un morceau depuis le menu contextuel"""
        if not messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer '{song['title']}'?"):
            return
        try:
            song_db.delete_song(song['id'])
            messagebox.showinfo("Succes", "Morceau supprime")
            self._load_songs()
            self._clear_form()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{e}")

    def _import_pdfs(self):
        """Importer plusieurs fichiers PDF en une fois"""
        filepaths = filedialog.askopenfilenames(
            title="Selectionner des fichiers PDF a importer",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
            initialdir=os.path.join(os.path.expanduser("~"), "Downloads")
        )
        if not filepaths:
            return
        try:
            result = song_db.import_pdf_files(list(filepaths))
            msg = f"{result['imported']} morceau(x) importe(s) avec succes."
            if result['errors']:
                msg += f"\n\n{len(result['errors'])} erreur(s):\n"
                msg += "\n".join(result['errors'][:5])
                if len(result['errors']) > 5:
                    msg += f"\n... et {len(result['errors']) - 5} autres"
            messagebox.showinfo("Import termine", msg)
            self._load_songs()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'import:\n{e}")

    def _close(self):
        """Fermer la fenetre"""
        if self.on_close:
            self.on_close()
        self.destroy()
