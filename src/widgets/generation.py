"""
Generation Panel - Step 4: Generate PDF and download
"""
import customtkinter as ctk
from typing import Callable, Dict, Any, List, Optional
import threading
import os


class GenerationPanel(ctk.CTkFrame):
    """Step 4: PDF generation with progress and download"""

    def __init__(self, parent, on_prev: Callable, get_all_config: Callable):
        super().__init__(parent, fg_color="transparent")

        self.on_prev = on_prev
        self.get_all_config = get_all_config
        self.generated_path: Optional[str] = None
        self.is_generating = False
        self.error_textbox = None

        self._create_widgets()

    def _create_widgets(self):
        """Create panel UI"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === Header ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text=" Génération du PDF",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        # Back button
        ctk.CTkButton(
            header,
            text="<- Précédent",
            width=100,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.on_prev
        ).pack(side="right")

        # === Content ===
        content = ctk.CTkFrame(self, corner_radius=10)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        content.grid_columnconfigure(0, weight=1)

        # --- Summary Section ---
        summary_frame = ctk.CTkFrame(content, fg_color="transparent")
        summary_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            summary_frame,
            text=" Récapitulatif",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", pady=(0, 10))

        self.summary_text = ctk.CTkLabel(
            summary_frame,
            text="Chargement...",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        )
        self.summary_text.pack(fill="x")

        # Separator
        ctk.CTkFrame(content, height=2, fg_color=("#e5e7eb", "#374151")).pack(
            fill="x", padx=20, pady=10
        )

        # --- Generation Section ---
        gen_frame = ctk.CTkFrame(content, fg_color="transparent")
        gen_frame.pack(fill="x", padx=20, pady=20)

        # Progress bar
        self.progress_label = ctk.CTkLabel(
            gen_frame,
            text="Prêt à générer",
            font=ctk.CTkFont(size=14)
        )
        self.progress_label.pack(pady=(0, 10))

        self.progress_bar = ctk.CTkProgressBar(gen_frame, width=400)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(
            gen_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("#6b7280", "#9ca3af")
        )
        self.status_label.pack(pady=5)

        # Generate button
        self.generate_btn = ctk.CTkButton(
            gen_frame,
            text=" Générer le PDF",
            width=200,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#16a34a",
            hover_color="#15803d",
            command=self._start_generation
        )
        self.generate_btn.pack(pady=20)

        # Separator
        ctk.CTkFrame(content, height=2, fg_color=("#e5e7eb", "#374151")).pack(
            fill="x", padx=20, pady=10
        )

        # --- Result Section ---
        self.result_frame = ctk.CTkFrame(content, fg_color="transparent")
        self.result_frame.pack(fill="x", padx=20, pady=20)

        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.result_label.pack(pady=10)

        # Action buttons (hidden until generation complete)
        self.action_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")

        ctk.CTkButton(
            self.action_frame,
            text=" Ouvrir le dossier",
            width=150,
            command=self._open_folder
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            self.action_frame,
            text=" Ouvrir le PDF",
            width=150,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            command=self._open_pdf
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            self.action_frame,
            text=" Nouveau Book",
            width=150,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self._new_book
        ).pack(side="left", padx=10)

    def update_summary(self):
        """Update the summary with current configuration"""
        config = self.get_all_config()

        song_count = len(config.get('songs', []))
        book_config = config.get('book_config', {})
        export_config = config.get('export_config', {})

        # Build summary text
        summary_lines = [
            f" Titre: {book_config.get('title', 'Sans titre')}",
            f" Instrument: {book_config.get('instrument', 'guitar').capitalize()}",
            f" Morceaux: {song_count}",
            "",
            "Options:",
        ]

        if book_config.get('include_cover'):
            summary_lines.append("  [x] Page de garde")
        if book_config.get('include_toc'):
            summary_lines.append("  [x] Table des matieres")
        if book_config.get('include_index_title'):
            summary_lines.append("  [x] Index par titre")
        if book_config.get('include_index_artist'):
            summary_lines.append("  [x] Index par artiste")
        if book_config.get('include_index_genre'):
            summary_lines.append("  [x] Index par genre")
        if book_config.get('page_numbers'):
            pos = book_config.get('page_number_position', 'center')
            pos_text = {'left': 'gauche', 'center': 'centre', 'right': 'droite'}.get(pos, pos)
            summary_lines.append(f"  [x] Numeros de page ({pos_text})")

        summary_lines.extend([
            "",
            f" Format: {export_config.get('page_format', 'A4')} ({export_config.get('orientation', 'portrait')})",
        ])

        self.summary_text.configure(text="\n".join(summary_lines))

    def _start_generation(self):
        """Start PDF generation in background thread"""
        if self.is_generating:
            return

        self.is_generating = True
        self.generate_btn.configure(state="disabled", text="Génération en cours...")
        self.progress_bar.set(0)
        self.progress_label.configure(text="Démarrage de la génération...")
        self.action_frame.pack_forget()

        # Run in thread
        thread = threading.Thread(target=self._generate_pdf, daemon=True)
        thread.start()

    def _generate_pdf(self):
        """Generate PDF (runs in background thread)"""
        try:
            config = self.get_all_config()
            songs = config.get('songs', [])
            book_config = config.get('book_config', {})
            export_config = config.get('export_config', {})

            # Update progress
            self._update_progress(0.1, "Préparation...")

            # Import generator
            import sys
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend', 'services'))
            from pdf_generator import MusicBookGenerator

            self._update_progress(0.2, "Chargement des morceaux...")

            # Create generator
            output_dir = export_config.get('output_dir') or None
            generator = MusicBookGenerator(output_dir=output_dir)

            self._update_progress(0.4, "Génération de la page de garde...")

            # Generate PDF with all options
            output_path = generator.generate_from_song_ids(
                song_ids=songs,
                title=book_config.get('title', 'Music Book'),
                instrument=book_config.get('instrument', 'guitar'),
                include_cover=book_config.get('include_cover', True),
                include_toc=book_config.get('include_toc', True),
                include_index=book_config.get('include_index_title', True),
                include_index_artist=book_config.get('include_index_artist', False),
                include_index_genre=book_config.get('include_index_genre', False),
                page_numbers=book_config.get('page_numbers', True),
                page_number_position=book_config.get('page_number_position', 'center'),
                page_format=export_config.get('page_format', 'A4'),
                orientation=export_config.get('orientation', 'portrait'),
                margin_top=export_config.get('margin_top', 20),
                margin_bottom=export_config.get('margin_bottom', 20),
                margin_left=export_config.get('margin_left', 15),
                margin_right=export_config.get('margin_right', 15),
                filename_pattern=export_config.get('filename_pattern', '{title}_{instrument}_{date}')
            )

            self._update_progress(0.9, "Sauvegarde du book...")

            # Sauvegarder le book dans la base de données
            self._db_save_error = None
            save_success = self._save_book_to_database(songs, book_config, output_path)

            self.generated_path = output_path
            self._update_progress(1.0, "Terminé!")

            # Show success (avec avertissement si échec sauvegarde BDD)
            if save_success:
                self.after(500, self._show_success)
            else:
                self.after(500, self._show_success_with_warning)

        except Exception as e:
            self.after(0, lambda: self._show_error(str(e)))

    def _save_book_to_database(self, song_ids: list, book_config: dict, output_path: str) -> bool:
        """Sauvegarde le book généré dans la base de données

        Returns:
            bool: True si sauvegarde réussie, False sinon
        """
        import sys
        import traceback
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

        try:
            from app import app, db
            from models.book import Book
            from models.book_song import BookSong

            with app.app_context():
                # Créer le book
                book = Book(
                    title=book_config.get('title', 'Music Book'),
                    instrument=book_config.get('instrument', 'guitar'),
                    include_cover=book_config.get('include_cover', True),
                    include_toc=book_config.get('include_toc', True),
                    include_index=book_config.get('include_index_title', True),
                    pdf_path=output_path
                )
                db.session.add(book)
                db.session.flush()  # Pour obtenir l'ID

                # Ajouter les morceaux au book
                for position, song_id in enumerate(song_ids, 1):
                    book_song = BookSong(
                        book_id=book.id,
                        song_id=song_id,
                        position=position
                    )
                    db.session.add(book_song)

                db.session.commit()
                print(f"[OK] Book sauvegardé: {book.title} (ID: {book.id}, instrument: {book.instrument})")
                return True

        except Exception as e:
            error_details = traceback.format_exc()
            print(f"[ERR] Erreur sauvegarde book: {e}")
            print(f"   Détails: {error_details}")
            # Stocker l'erreur pour affichage dans l'UI
            self._db_save_error = str(e)
            return False

    def _update_progress(self, value: float, status: str):
        """Update progress bar and status (thread-safe)"""
        self.after(0, lambda: self.progress_bar.set(value))
        self.after(0, lambda: self.status_label.configure(text=status))
        self.after(0, lambda: self.progress_label.configure(text=f"Génération... {int(value*100)}%"))

    def _show_success(self):
        """Show success message and action buttons"""
        self.is_generating = False
        self.generate_btn.configure(state="normal", text="Générer le PDF")
        self.progress_label.configure(text="PDF généré avec succès!")
        self.result_label.configure(
            text=f"[OK] {os.path.basename(self.generated_path)}",
            text_color=("#16a34a", "#22c55e")
        )
        self.action_frame.pack(pady=10)

        # Rafraîchir la liste des books
        if hasattr(self, '_refresh_books_callback') and self._refresh_books_callback:
            self._refresh_books_callback()

    def _show_success_with_warning(self):
        """Show success message with database save warning"""
        self.is_generating = False
        self.generate_btn.configure(state="normal", text="Générer le PDF")
        self.progress_label.configure(text="PDF genere (WARN: non enregistre en BDD)")

        error_msg = getattr(self, '_db_save_error', 'Erreur inconnue')
        self.result_label.configure(
            text=f"WARN: {os.path.basename(self.generated_path)}\n   Erreur BDD: {error_msg}",
            text_color=("#f59e0b", "#fbbf24")
        )
        self.action_frame.pack(pady=10)

        # Ne pas rafraîchir la liste car le book n'a pas été sauvegardé
        print(f"⚠️ PDF généré mais non enregistré en base de données: {error_msg}")

    def _show_error(self, error: str):
        """Show error message with copyable text"""
        self.is_generating = False
        self.generate_btn.configure(state="normal", text="Générer le PDF")
        self.progress_label.configure(text="[ERR] Erreur lors de la génération")
        self.status_label.configure(text="")
        self.result_label.configure(
            text="La génération a échoué. Erreur ci-dessous (sélectionnable) :",
            text_color=("#ef4444", "#f87171")
        )

        # Zone de texte copiable pour l'erreur
        self._show_copyable_error(error)

    def _show_copyable_error(self, error: str):
        """Affiche l'erreur dans une zone copiable"""
        # Supprimer l'ancien widget d'erreur s'il existe
        if hasattr(self, 'error_textbox') and self.error_textbox:
            self.error_textbox.destroy()

        self.error_textbox = ctk.CTkTextbox(
            self.result_frame,
            height=80,
            width=500,
            font=ctk.CTkFont(size=11, family="monospace"),
            fg_color=("#fef2f2", "#451a1a"),
            text_color=("#dc2626", "#fca5a5"),
            border_width=1,
            border_color=("#fecaca", "#7f1d1d")
        )
        self.error_textbox.pack(pady=10, fill="x", padx=10)
        self.error_textbox.insert("1.0", error)
        self.error_textbox.configure(state="normal")  # Permet la sélection

    def _open_folder(self):
        """Open output folder"""
        if self.generated_path:
            folder = os.path.dirname(self.generated_path)
            import subprocess
            subprocess.run(['xdg-open', folder], check=False)

    def _open_pdf(self):
        """Open generated PDF"""
        if self.generated_path:
            import subprocess
            subprocess.run(['xdg-open', self.generated_path], check=False)

    def _new_book(self):
        """Start new book (go back to step 1)"""
        if hasattr(self, '_new_book_callback') and self._new_book_callback:
            self._new_book_callback()

    def reset(self):
        """Reset panel state"""
        self.generated_path = None
        self.is_generating = False
        self.progress_bar.set(0)
        self.progress_label.configure(text="Prêt à générer")
        self.status_label.configure(text="")
        self.result_label.configure(text="")
        self.action_frame.pack_forget()
        self.generate_btn.configure(state="normal", text="Générer le PDF")

        # Supprimer le widget d'erreur s'il existe
        if hasattr(self, 'error_textbox') and self.error_textbox:
            self.error_textbox.destroy()
            self.error_textbox = None
