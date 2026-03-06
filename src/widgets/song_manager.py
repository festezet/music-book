"""
Song Manager - Gestion de la bibliotheque de morceaux
Permet d'ajouter, editer et supprimer des morceaux
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from typing import Callable, Optional, Dict, Any, List
import os
import json


class SongManagerDialog(ctk.CTkToplevel):
    """Fenetre de gestion de la bibliotheque de morceaux"""

    GENRE_OPTIONS = [
        "Rock",
        "Pop",
        "Chanson Francaise",
        "Blues",
        "Jazz",
        "Folk",
        "Country",
        "Metal",
        "Classique",
        "Reggae",
        "Funk",
        "Soul",
        "Variete",
        "Autre"
    ]

    SOURCE_OPTIONS = [
        ("Ultimate Guitar", "ultimate_guitar"),
        ("Songsterr", "songsterr"),
        ("Boite a chansons", "boite_chansons"),
        ("Autre", "other")
    ]

    INSTRUMENT_OPTIONS = [
        ("Guitare", "guitar"),
        ("Basse", "bass"),
        ("Violon", "violin"),
        ("Piano", "piano"),
        ("Ukulele", "ukulele")
    ]

    TYPE_OPTIONS = [
        ("Accords", "chords"),
        ("Tablature", "tab"),
        ("Partition", "sheet")
    ]

    def __init__(self, parent, on_close: Callable = None):
        super().__init__(parent)

        self.on_close = on_close
        self.selected_song_id: Optional[int] = None
        self.all_songs: List[Dict[str, Any]] = []

        # Configuration fenetre
        self.title("Gestion de la Bibliotheque")
        self.geometry("1200x700")
        self.minsize(1000, 600)

        # Modal
        self.transient(parent)

        self._create_widgets()
        self._load_songs()

        # Attendre que la fenetre soit visible avant grab_set
        self.after(100, self._make_modal)

    def _make_modal(self):
        """Rendre la fenetre modale apres affichage"""
        try:
            self.grab_set()
        except Exception:
            pass  # Ignorer si echec

    def _create_widgets(self):
        """Creer l'interface"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(1, weight=1)

        # === Header ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            header,
            text="Gestion de la Bibliotheque",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Fermer",
            width=100,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self._close
        ).pack(side="right")

        # === Liste des morceaux (gauche) ===
        list_frame = ctk.CTkFrame(self, corner_radius=10)
        list_frame.grid(row=1, column=0, sticky="nsew", padx=(20, 10), pady=10)
        list_frame.grid_rowconfigure(2, weight=1)  # Liste sur row 2
        list_frame.grid_columnconfigure(0, weight=1)

        # Header liste (row 0)
        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))

        ctk.CTkLabel(
            list_header,
            text="Morceaux",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")

        self.song_count_label = ctk.CTkLabel(
            list_header,
            text="(0)",
            font=ctk.CTkFont(size=12),
            text_color=("#6b7280", "#9ca3af")
        )
        self.song_count_label.pack(side="left", padx=5)

        ctk.CTkButton(
            list_header,
            text="Importer PDFs",
            width=110,
            fg_color="#16a34a",
            hover_color="#15803d",
            command=self._import_pdfs
        ).pack(side="right")

        # Recherche (row 1)
        search_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        search_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *args: self._filter_songs())
        ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Rechercher...",
            width=200
        ).pack(fill="x")

        # Liste scrollable (row 2)
        self.song_list = ctk.CTkScrollableFrame(list_frame, width=350)
        self.song_list.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
        self.song_list.grid_columnconfigure(0, weight=1)

        # === Formulaire d'edition (droite) ===
        form_frame = ctk.CTkFrame(self, corner_radius=10)
        form_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 20), pady=10)
        form_frame.grid_columnconfigure(1, weight=1)

        # Titre formulaire
        self.form_title = ctk.CTkLabel(
            form_frame,
            text="Nouveau morceau",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.form_title.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(15, 20))

        # Champs du formulaire
        row = 1

        # Titre
        ctk.CTkLabel(form_frame, text="Titre *").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.title_entry = ctk.CTkEntry(form_frame, width=300)
        self.title_entry.grid(row=row, column=1, sticky="ew", padx=20, pady=5)
        row += 1

        # Artiste
        ctk.CTkLabel(form_frame, text="Artiste").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.artist_entry = ctk.CTkEntry(form_frame, width=300)
        self.artist_entry.grid(row=row, column=1, sticky="ew", padx=20, pady=5)
        row += 1

        # Genre
        ctk.CTkLabel(form_frame, text="Genre").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.genre_var = ctk.StringVar(value="")
        self.genre_menu = ctk.CTkOptionMenu(
            form_frame,
            values=self.GENRE_OPTIONS,
            variable=self.genre_var,
            width=200
        )
        self.genre_menu.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        # Source
        ctk.CTkLabel(form_frame, text="Source").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.source_var = ctk.StringVar(value="")
        self.source_menu = ctk.CTkOptionMenu(
            form_frame,
            values=[s[0] for s in self.SOURCE_OPTIONS],
            variable=self.source_var,
            width=200
        )
        self.source_menu.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        # Type
        ctk.CTkLabel(form_frame, text="Type").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.type_var = ctk.StringVar(value="")
        self.type_menu = ctk.CTkOptionMenu(
            form_frame,
            values=[t[0] for t in self.TYPE_OPTIONS],
            variable=self.type_var,
            width=200
        )
        self.type_menu.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        # Instruments (checkboxes)
        ctk.CTkLabel(form_frame, text="Instruments").grid(row=row, column=0, sticky="nw", padx=20, pady=5)
        inst_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        inst_frame.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        self.instrument_vars = {}
        for i, (label, value) in enumerate(self.INSTRUMENT_OPTIONS):
            var = ctk.BooleanVar(value=False)
            self.instrument_vars[value] = var
            ctk.CTkCheckBox(inst_frame, text=label, variable=var).grid(row=0, column=i, padx=5)
        row += 1

        # Fichier PDF
        ctk.CTkLabel(form_frame, text="Fichier PDF *").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        pdf_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        pdf_frame.grid(row=row, column=1, sticky="ew", padx=20, pady=5)
        pdf_frame.grid_columnconfigure(0, weight=1)

        self.pdf_path_var = ctk.StringVar()
        self.pdf_entry = ctk.CTkEntry(pdf_frame, textvariable=self.pdf_path_var, state="readonly")
        self.pdf_entry.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(
            pdf_frame,
            text="Parcourir...",
            width=100,
            command=self._browse_pdf
        ).grid(row=0, column=1, padx=(10, 0))
        row += 1

        # Nombre de pages
        ctk.CTkLabel(form_frame, text="Nombre de pages").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.pages_entry = ctk.CTkEntry(form_frame, width=80)
        self.pages_entry.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        # Tonalite
        ctk.CTkLabel(form_frame, text="Tonalite").grid(row=row, column=0, sticky="w", padx=20, pady=5)
        self.key_entry = ctk.CTkEntry(form_frame, width=80, placeholder_text="ex: Am, G, D")
        self.key_entry.grid(row=row, column=1, sticky="w", padx=20, pady=5)
        row += 1

        # Notes
        ctk.CTkLabel(form_frame, text="Notes").grid(row=row, column=0, sticky="nw", padx=20, pady=5)
        self.notes_entry = ctk.CTkTextbox(form_frame, height=60)
        self.notes_entry.grid(row=row, column=1, sticky="ew", padx=20, pady=5)
        row += 1

        # Boutons d'action
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=row, column=0, columnspan=2, pady=20)

        self.save_btn = ctk.CTkButton(
            btn_frame,
            text="Enregistrer",
            width=120,
            fg_color="#16a34a",
            hover_color="#15803d",
            command=self._save_song
        )
        self.save_btn.pack(side="left", padx=10)

        self.delete_btn = ctk.CTkButton(
            btn_frame,
            text="Supprimer",
            width=120,
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self._delete_song
        )
        self.delete_btn.pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="Annuler",
            width=120,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self._clear_form
        ).pack(side="left", padx=10)

    def _load_songs(self):
        """Charger les morceaux depuis la base"""
        import sys
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        try:
            from app import app, db
            from models.song import Song

            with app.app_context():
                songs = Song.query.order_by(Song.title).all()
                self.all_songs = [s.to_dict() for s in songs]
                print(f"[SongManager] Charge {len(self.all_songs)} morceaux")
        except Exception as e:
            print(f"[SongManager] Erreur chargement morceaux: {e}")
            import traceback
            traceback.print_exc()
            self.all_songs = []

        self._update_song_list()

    def _filter_songs(self):
        """Filtrer la liste selon la recherche"""
        self._update_song_list()

    def _update_song_list(self):
        """Mettre a jour l'affichage de la liste"""
        # Vider la liste
        for widget in self.song_list.winfo_children():
            widget.destroy()

        search = self.search_var.get().lower()
        filtered = [
            s for s in self.all_songs
            if not search or search in s['title'].lower() or search in (s.get('artist') or '').lower()
        ]

        self.song_count_label.configure(text=f"({len(filtered)})")

        for song in filtered:
            self._create_song_item(song)

    def _create_song_item(self, song: Dict):
        """Creer un element de liste pour un morceau"""
        is_selected = self.selected_song_id == song['id']

        # Different colors for selected vs normal
        if is_selected:
            fg_color = ("#3b82f6", "#2563eb")  # Blue for selected
        else:
            fg_color = ("#f3f4f6", "#374151")  # Default gray

        item = ctk.CTkFrame(self.song_list, corner_radius=6, fg_color=fg_color, height=50)
        item.pack(fill="x", pady=2, padx=2, expand=True)
        item.bind("<Button-1>", lambda e, s=song: self._select_song(s))
        item.bind("<Button-3>", lambda e, s=song: self._show_context_menu(e, s))

        content = ctk.CTkFrame(item, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)
        content.bind("<Button-1>", lambda e, s=song: self._select_song(s))
        content.bind("<Button-3>", lambda e, s=song: self._show_context_menu(e, s))

        # Text color based on selection
        text_color = ("white", "white") if is_selected else None
        sub_text_color = ("#e5e7eb", "#d1d5db") if is_selected else ("#6b7280", "#9ca3af")

        # Instrument badge (colored) - BEFORE song info for visibility
        instruments = song.get('instruments') or []
        if instruments:
            inst_colors = {
                'guitar': ("#22c55e", "#16a34a"),  # Green
                'bass': ("#f59e0b", "#d97706"),    # Orange/Amber
                'violin': ("#8b5cf6", "#7c3aed"),  # Purple
                'piano': ("#ec4899", "#db2777"),   # Pink
                'ukulele': ("#06b6d4", "#0891b2")  # Cyan
            }
            inst_labels = {
                'guitar': 'GTR',
                'bass': 'BASS',
                'violin': 'VLN',
                'piano': 'PNO',
                'ukulele': 'UKE'
            }
            for inst in instruments:
                color = inst_colors.get(inst, ("#6b7280", "#4b5563"))
                label = inst_labels.get(inst, inst[:3].upper())
                badge = ctk.CTkLabel(
                    content,
                    text=label,
                    font=ctk.CTkFont(size=9, weight="bold"),
                    fg_color=color,
                    text_color="white",
                    corner_radius=4,
                    width=35,
                    height=18
                )
                badge.pack(side="left", padx=(0, 8))
                badge.bind("<Button-1>", lambda e, s=song: self._select_song(s))
                badge.bind("<Button-3>", lambda e, s=song: self._show_context_menu(e, s))

        # Song info frame
        info_frame = ctk.CTkFrame(content, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        info_frame.bind("<Button-1>", lambda e, s=song: self._select_song(s))
        info_frame.bind("<Button-3>", lambda e, s=song: self._show_context_menu(e, s))

        # Titre
        title_label = ctk.CTkLabel(
            info_frame,
            text=song['title'],
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=text_color,
            anchor="w"
        )
        title_label.pack(fill="x")
        title_label.bind("<Button-1>", lambda e, s=song: self._select_song(s))
        title_label.bind("<Button-3>", lambda e, s=song: self._show_context_menu(e, s))

        # Artiste + genre
        meta_parts = []
        if song.get('artist'):
            meta_parts.append(song['artist'])
        if song.get('genre'):
            meta_parts.append(song['genre'])
        meta_text = " - ".join(meta_parts) if meta_parts else "Sans artiste"

        meta_label = ctk.CTkLabel(
            info_frame,
            text=meta_text,
            font=ctk.CTkFont(size=10),
            text_color=sub_text_color,
            anchor="w"
        )
        meta_label.pack(fill="x")
        meta_label.bind("<Button-1>", lambda e, s=song: self._select_song(s))
        meta_label.bind("<Button-3>", lambda e, s=song: self._show_context_menu(e, s))

    def _show_context_menu(self, event, song: Dict):
        """Afficher le menu contextuel pour un morceau"""
        import tkinter as tk

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="Ouvrir le PDF",
            command=lambda: self._open_pdf(song)
        )
        menu.add_command(
            label="Ouvrir le dossier",
            command=lambda: self._open_folder(song)
        )
        menu.add_separator()
        menu.add_command(
            label="Editer",
            command=lambda: self._select_song(song)
        )
        menu.add_command(
            label="Supprimer",
            command=lambda: self._delete_song_direct(song)
        )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _open_pdf(self, song: Dict):
        """Ouvrir le fichier PDF du morceau"""
        pdf_path = song.get('pdf_path')
        if pdf_path and os.path.exists(pdf_path):
            import subprocess
            subprocess.run(['xdg-open', pdf_path], check=False)
        else:
            messagebox.showwarning("Attention", f"Fichier PDF introuvable:\n{pdf_path}")

    def _open_folder(self, song: Dict):
        """Ouvrir le dossier contenant le PDF"""
        pdf_path = song.get('pdf_path')
        if pdf_path:
            folder = os.path.dirname(pdf_path)
            if os.path.exists(folder):
                import subprocess
                subprocess.run(['xdg-open', folder], check=False)
            else:
                messagebox.showwarning("Attention", f"Dossier introuvable:\n{folder}")

    def _delete_song_direct(self, song: Dict):
        """Supprimer un morceau directement depuis le menu contextuel"""
        if not messagebox.askyesno("Confirmation", f"Voulez-vous vraiment supprimer '{song['title']}'?"):
            return

        import sys
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        try:
            from app import app, db
            from models.song import Song

            with app.app_context():
                s = Song.query.get(song['id'])
                if s:
                    db.session.delete(s)
                    db.session.commit()
                    messagebox.showinfo("Succes", "Morceau supprime")

            self._load_songs()
            self._clear_form()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{e}")

    def _select_song(self, song: Dict):
        """Selectionner un morceau pour edition"""
        self.selected_song_id = song['id']
        self.form_title.configure(text=f"Modifier: {song['title']}")

        # Remplir le formulaire
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, song.get('title', ''))

        self.artist_entry.delete(0, "end")
        self.artist_entry.insert(0, song.get('artist') or '')

        self.genre_var.set(song.get('genre') or self.GENRE_OPTIONS[0])

        # Source
        source = song.get('source') or ''
        source_label = next((s[0] for s in self.SOURCE_OPTIONS if s[1] == source), self.SOURCE_OPTIONS[0][0])
        self.source_var.set(source_label)

        # Type
        song_type = song.get('type') or ''
        type_label = next((t[0] for t in self.TYPE_OPTIONS if t[1] == song_type), self.TYPE_OPTIONS[0][0])
        self.type_var.set(type_label)

        # Instruments
        instruments = song.get('instruments') or []
        for inst, var in self.instrument_vars.items():
            var.set(inst in instruments)

        self.pdf_path_var.set(song.get('pdf_path') or '')

        self.pages_entry.delete(0, "end")
        self.pages_entry.insert(0, str(song.get('pages') or 1))

        self.key_entry.delete(0, "end")
        self.key_entry.insert(0, song.get('key') or '')

        self.notes_entry.delete("1.0", "end")
        self.notes_entry.insert("1.0", song.get('notes') or '')

        self.delete_btn.configure(state="normal")

    def _new_song(self):
        """Preparer le formulaire pour un nouveau morceau"""
        self._clear_form()
        self.form_title.configure(text="Nouveau morceau")

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
            initialdir="/home/fabrice-ryzen/Downloads/Chords"
        )
        if filepath:
            self.pdf_path_var.set(filepath)

            # Tenter de detecter le nombre de pages
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(filepath)
                pages = len(reader.pages)
                self.pages_entry.delete(0, "end")
                self.pages_entry.insert(0, str(pages))
            except:
                pass

            # Pre-remplir le titre depuis le nom du fichier si vide
            if not self.title_entry.get().strip():
                filename = os.path.basename(filepath)
                # Enlever l'extension .pdf
                title = os.path.splitext(filename)[0]
                self.title_entry.delete(0, "end")
                self.title_entry.insert(0, title)

    def _import_pdfs(self):
        """Importer plusieurs fichiers PDF en une fois"""
        filepaths = filedialog.askopenfilenames(
            title="Selectionner des fichiers PDF a importer",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
            initialdir="/home/fabrice-ryzen/Downloads/Chords"
        )

        if not filepaths:
            return

        import sys
        backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
        if backend_path not in sys.path:
            sys.path.insert(0, backend_path)

        imported = 0
        errors = []

        try:
            from app import app, db
            from models.song import Song
            from PyPDF2 import PdfReader

            with app.app_context():
                for filepath in filepaths:
                    try:
                        # Extraire le titre du nom de fichier
                        filename = os.path.basename(filepath)
                        title = os.path.splitext(filename)[0]

                        # Detecter le nombre de pages
                        try:
                            reader = PdfReader(filepath)
                            pages = len(reader.pages)
                        except:
                            pages = 1

                        # Detecter la source depuis le nom de fichier
                        source = None
                        if "Ultimate Guitar" in filename or "tabs @" in filename:
                            source = "ultimate_guitar"
                        elif "Songsterr" in filename:
                            source = "songsterr"
                        elif "Boîte à chansons" in filename or "Boite a chansons" in filename:
                            source = "boite_chansons"

                        # Detecter le type
                        song_type = None
                        if "Tab" in filename or "_tab" in filename.lower():
                            song_type = "tab"
                        elif "Chord" in filename or "_chord" in filename.lower():
                            song_type = "chords"

                        # Detecter l'instrument depuis le nom
                        instruments = []
                        if "_bass" in filename.lower() or "Bass Tab" in filename:
                            instruments.append("bass")
                        elif "_guitare" in filename.lower() or "Guitar" in filename:
                            instruments.append("guitar")
                        else:
                            instruments.append("guitar")  # Par defaut

                        # Creer le morceau
                        song = Song(
                            title=title,
                            pdf_path=filepath,
                            pages=pages,
                            source=source,
                            type=song_type,
                            instruments=json.dumps(instruments) if instruments else None
                        )
                        db.session.add(song)
                        imported += 1

                    except Exception as e:
                        errors.append(f"{os.path.basename(filepath)}: {e}")

                db.session.commit()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'import:\n{e}")
            return

        # Afficher le resultat
        msg = f"{imported} morceau(x) importe(s) avec succes."
        if errors:
            msg += f"\n\n{len(errors)} erreur(s):\n" + "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n... et {len(errors) - 5} autres"

        messagebox.showinfo("Import termine", msg)
        self._load_songs()

    def _save_song(self):
        """Enregistrer le morceau"""
        title = self.title_entry.get().strip()
        pdf_path = self.pdf_path_var.get().strip()

        if not title:
            messagebox.showerror("Erreur", "Le titre est obligatoire")
            return

        if not pdf_path:
            messagebox.showerror("Erreur", "Le fichier PDF est obligatoire")
            return

        if not os.path.exists(pdf_path):
            messagebox.showerror("Erreur", f"Le fichier PDF n'existe pas:\n{pdf_path}")
            return

        # Recuperer les valeurs
        artist = self.artist_entry.get().strip() or None
        genre = self.genre_var.get() if self.genre_var.get() != self.GENRE_OPTIONS[0] else None

        source = None
        for label, value in self.SOURCE_OPTIONS:
            if label == self.source_var.get():
                source = value
                break

        song_type = None
        for label, value in self.TYPE_OPTIONS:
            if label == self.type_var.get():
                song_type = value
                break

        instruments = [inst for inst, var in self.instrument_vars.items() if var.get()]

        try:
            pages = int(self.pages_entry.get()) if self.pages_entry.get() else 1
        except ValueError:
            pages = 1

        key = self.key_entry.get().strip() or None
        notes = self.notes_entry.get("1.0", "end").strip() or None

        # Sauvegarder
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

        try:
            from app import app, db
            from models.song import Song

            with app.app_context():
                if self.selected_song_id:
                    # Mise a jour
                    song = Song.query.get(self.selected_song_id)
                    if song:
                        song.title = title
                        song.artist = artist
                        song.genre = genre
                        song.source = source
                        song.type = song_type
                        song.instruments = json.dumps(instruments) if instruments else None
                        song.pdf_path = pdf_path
                        song.pages = pages
                        song.key = key
                        song.notes = notes
                        db.session.commit()
                        messagebox.showinfo("Succes", f"Morceau '{title}' mis a jour")
                else:
                    # Nouveau
                    song = Song(
                        title=title,
                        artist=artist,
                        genre=genre,
                        source=source,
                        type=song_type,
                        instruments=json.dumps(instruments) if instruments else None,
                        pdf_path=pdf_path,
                        pages=pages,
                        key=key,
                        notes=notes
                    )
                    db.session.add(song)
                    db.session.commit()
                    messagebox.showinfo("Succes", f"Morceau '{title}' ajoute")

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

        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

        try:
            from app import app, db
            from models.song import Song

            with app.app_context():
                song = Song.query.get(self.selected_song_id)
                if song:
                    db.session.delete(song)
                    db.session.commit()
                    messagebox.showinfo("Succes", "Morceau supprime")

            self._load_songs()
            self._clear_form()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{e}")

    def _close(self):
        """Fermer la fenetre"""
        if self.on_close:
            self.on_close()
        self.destroy()
