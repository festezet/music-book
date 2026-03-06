#!/usr/bin/env python3
"""
Music Book Generator - Workflow GUI
CustomTkinter-based visual workflow interface for creating music books

Features:
- Visual vertical workflow with 4 steps
- Song library with sorting and filtering
- Book configuration (TOC, indexes, page numbers)
- PDF export options
- Generation with progress tracking

Usage:
    python3 workflow_gui.py
    # or
    ./lancer_music_book_workflow.sh
"""
import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "backend"))

import customtkinter as ctk
from typing import Optional, Dict, Any, List

from widgets.workflow_sidebar import WorkflowSidebar
from widgets.song_library import SongLibraryPanel
from widgets.book_config import BookConfigPanel
from widgets.export_options import ExportOptionsPanel
from widgets.generation import GenerationPanel
from widgets.book_list import BookListPanel
from widgets.song_manager import SongManagerDialog


class MusicBookWorkflowApp(ctk.CTk):
    """Main application window for Music Book Generator"""

    def __init__(self):
        super().__init__()

        # Window configuration
        self.title("Music Book Generator - Workflow")
        self.geometry("1400x1000")
        self.minsize(1200, 850)

        # Theme configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # State
        self.current_step = 1
        self.current_book_id: Optional[int] = None
        self.selected_songs: List[int] = []

        # Create UI
        self._create_layout()

    def _create_layout(self):
        """Create main application layout"""
        # Configure grid
        self.grid_columnconfigure(0, weight=0)  # Sidebar fixed
        self.grid_columnconfigure(1, weight=0)  # Book list fixed
        self.grid_columnconfigure(2, weight=1)  # Content expands
        self.grid_rowconfigure(0, weight=0)     # Header fixed
        self.grid_rowconfigure(1, weight=1)     # Content expands
        self.grid_rowconfigure(2, weight=0)     # Footer fixed

        # === Header ===
        self._create_header()

        # === Main Content Area ===
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)
        main_frame.grid_columnconfigure(0, weight=0)  # Sidebar
        main_frame.grid_columnconfigure(1, weight=0)  # Book list
        main_frame.grid_columnconfigure(2, weight=1)  # Step content
        main_frame.grid_rowconfigure(0, weight=1)

        # Left: Workflow Sidebar
        self.sidebar = WorkflowSidebar(main_frame, callback=self._on_step_click, width=180)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 10))

        # Middle: Book List
        self.book_list = BookListPanel(
            main_frame,
            on_select=self._on_book_select,
            on_new=self._on_new_book,
            on_rename=self._on_book_rename,
            width=250
        )
        self.book_list.grid(row=0, column=1, sticky="ns", padx=(0, 10))

        # Right: Step Content Panels
        self.content_frame = ctk.CTkFrame(main_frame, corner_radius=10)
        self.content_frame.grid(row=0, column=2, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Create step panels
        self.step_panels: Dict[int, ctk.CTkFrame] = {
            1: SongLibraryPanel(
                self.content_frame,
                on_next=lambda: self._advance_step(),
                get_selected=self._get_selected_songs,
                on_book_name_change=self._on_book_name_change,
                on_selection_change=self._update_song_count
            ),
            2: BookConfigPanel(
                self.content_frame,
                on_next=lambda: self._advance_step(),
                on_prev=lambda: self._go_to_step(1),
                get_config=self._get_book_config
            ),
            3: ExportOptionsPanel(
                self.content_frame,
                on_next=lambda: self._advance_step(),
                on_prev=lambda: self._go_to_step(2),
                get_config=self._get_export_config
            ),
            4: GenerationPanel(
                self.content_frame,
                on_prev=lambda: self._go_to_step(3),
                get_all_config=self._get_all_config
            ),
        }

        # Connect generation panel's callbacks
        self.step_panels[4]._new_book_callback = self._on_new_book
        self.step_panels[4]._refresh_books_callback = self._refresh_book_list

        # === Footer ===
        self._create_footer()

        # Show step 1
        self._show_step(1)

    def _create_header(self):
        """Create application header"""
        header = ctk.CTkFrame(self, height=60, corner_radius=0)
        header.grid(row=0, column=0, columnspan=3, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        # Logo/Title
        title = ctk.CTkLabel(
            header,
            text="Music Book Generator",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#2563eb", "#60a5fa")
        )
        title.grid(row=0, column=0, padx=20, pady=15)

        subtitle = ctk.CTkLabel(
            header,
            text="Creez vos recueils de partitions",
            font=ctk.CTkFont(size=13),
            text_color=("#6b7280", "#9ca3af")
        )
        subtitle.grid(row=0, column=1, padx=10, pady=15, sticky="w")

        # Bouton Gerer Bibliotheque
        library_btn = ctk.CTkButton(
            header,
            text="Gerer Bibliotheque",
            width=150,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self._open_song_manager
        )
        library_btn.grid(row=0, column=2, padx=10, pady=15)

        # Step indicator
        self.step_indicator = ctk.CTkLabel(
            header,
            text="Etape 1/4",
            font=ctk.CTkFont(size=12),
            text_color=("#9ca3af", "#6b7280")
        )
        self.step_indicator.grid(row=0, column=3, padx=20, pady=15)

    def _create_footer(self):
        """Create application footer"""
        footer = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color="transparent")
        footer.grid(row=2, column=0, columnspan=3, sticky="ew", pady=5)

        # Status
        self.status_label = ctk.CTkLabel(
            footer,
            text="Prêt",
            font=ctk.CTkFont(size=11),
            text_color=("#6b7280", "#9ca3af")
        )
        self.status_label.pack(side="left", padx=20)

        # Song count
        self.song_count_label = ctk.CTkLabel(
            footer,
            text="0 morceaux sélectionnés",
            font=ctk.CTkFont(size=11),
            text_color=("#6b7280", "#9ca3af")
        )
        self.song_count_label.pack(side="right", padx=20)

    # =========================================================================
    # NAVIGATION
    # =========================================================================

    def _show_step(self, step: int):
        """Display the specified step panel"""
        # Hide all panels
        for panel in self.step_panels.values():
            panel.grid_forget()

        # Show selected panel
        if step in self.step_panels:
            self.step_panels[step].grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.current_step = step
        self.sidebar.set_active_step(step)

        # Update header
        step_names = {1: "Selection", 2: "Configuration", 3: "Export", 4: "Generation"}
        self.step_indicator.configure(text=f"Etape {step}/4 - {step_names.get(step, '')}")

        # Update status
        self.status_label.configure(text=f"Etape {step}: {step_names.get(step, '')}")

        # Update song count
        self._update_song_count()

        # Special handling for step 4
        if step == 4:
            self.step_panels[4].update_summary()

    def _on_step_click(self, step_number: int):
        """Handle click on workflow node"""
        if step_number <= self.current_step:
            self._go_to_step(step_number)

    def _go_to_step(self, step: int):
        """Navigate to a specific step"""
        # Save state before changing step
        if self.current_step == 1:
            self.selected_songs = self.step_panels[1].get_selected_songs()

        self._show_step(step)

    def _advance_step(self):
        """Move to next step in workflow"""
        if self.current_step < 4:
            # Save current step state
            if self.current_step == 1:
                self.selected_songs = self.step_panels[1].get_selected_songs()
                if not self.selected_songs:
                    self._show_warning("Sélectionnez au moins un morceau")
                    return

                # Sauvegarder en BDD si book existant
                if self.current_book_id:
                    self._save_book_songs(self.current_book_id, self.selected_songs)

            self._show_step(self.current_step + 1)

    # =========================================================================
    # DATA GETTERS
    # =========================================================================

    def _get_selected_songs(self) -> List[int]:
        """Get selected song IDs"""
        return self.step_panels[1].get_selected_songs()

    def _get_book_config(self) -> Dict[str, Any]:
        """Get book configuration"""
        return self.step_panels[2].get_configuration()

    def _get_export_config(self) -> Dict[str, Any]:
        """Get export configuration"""
        return self.step_panels[3].get_export_config()

    def _get_all_config(self) -> Dict[str, Any]:
        """Get all configuration for generation"""
        return {
            'songs': self._get_selected_songs(),
            'book_config': self._get_book_config(),
            'export_config': self._get_export_config(),
        }

    def _update_song_count(self):
        """Update the song count in footer and book card"""
        count = len(self._get_selected_songs())
        text = f"{count} morceau{'x' if count > 1 else ''} sélectionné{'s' if count > 1 else ''}"
        self.song_count_label.configure(text=text)

        # Also update the book card if a book is selected
        if self.current_book_id:
            self.book_list.update_song_count(self.current_book_id, count)

    # =========================================================================
    # BOOK MANAGEMENT
    # =========================================================================

    def _on_book_select(self, book_id: int, book_data: Dict[str, Any]):
        """Handle book selection from list"""
        import time
        t_start = time.time()

        # Sauvegarder les changements du book actuel avant de changer
        if self.current_book_id and self.current_book_id != book_id:
            current_songs = self.step_panels[1].get_selected_songs()
            self._save_book_songs(self.current_book_id, current_songs)
        t1 = time.time()

        self.current_book_id = book_id

        # Charger les morceaux du book depuis la BDD
        song_ids = self._load_book_songs(book_id)
        t2 = time.time()

        # Mettre à jour le nom du book dans le panel de sélection
        self.step_panels[1].set_book_name(book_data.get('title', 'Music Book'))

        # Mettre à jour le panel de sélection des morceaux
        self.step_panels[1].set_selected_songs(song_ids)
        t3 = time.time()

        self.selected_songs = song_ids

        # Charger la configuration du book dans le panel config
        book_config = {
            'title': book_data.get('title', 'Music Book'),
            'instrument': book_data.get('instrument', 'guitar'),
            'include_cover': book_data.get('include_cover', True),
            'include_toc': book_data.get('include_toc', True),
            'include_index_title': book_data.get('include_index', True),
        }
        self.step_panels[2].set_configuration(book_config)

        # Reset le panel de génération
        self.step_panels[4].reset()

        # Mettre à jour le compteur
        self._update_song_count()

        t_end = time.time()
        print(f"⏱️ _on_book_select: save_prev={t1-t_start:.3f}s, load_db={t2-t1:.3f}s, set_songs={t3-t2:.3f}s, TOTAL={t_end-t_start:.3f}s")

        self.status_label.configure(
            text=f"Book chargé: {book_data.get('title', '')} ({len(song_ids)} morceaux)"
        )

    def _load_book_songs(self, book_id: int) -> List[int]:
        """Charge les song_ids d'un book depuis la BDD"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

        try:
            from app import app, db
            from models.book_song import BookSong

            with app.app_context():
                book_songs = BookSong.query.filter_by(book_id=book_id)\
                    .order_by(BookSong.position).all()
                return [bs.song_id for bs in book_songs]
        except Exception as e:
            print(f"Erreur chargement morceaux du book: {e}")
            return []

    def _save_book_songs(self, book_id: int, song_ids: List[int]) -> bool:
        """Sauvegarde les morceaux d'un book dans la BDD"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

        try:
            from app import app, db
            from models.book_song import BookSong

            with app.app_context():
                # Supprimer les anciennes associations
                BookSong.query.filter_by(book_id=book_id).delete()

                # Ajouter les nouvelles
                for position, song_id in enumerate(song_ids, 1):
                    book_song = BookSong(
                        book_id=book_id,
                        song_id=song_id,
                        position=position
                    )
                    db.session.add(book_song)

                db.session.commit()
                print(f"✅ Book {book_id} sauvegardé: {len(song_ids)} morceaux")
                return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde morceaux: {e}")
            return False

    def _on_new_book(self):
        """Handle new book creation - creates a new book in DB with default name"""
        # Generate default name with incrementing number
        default_name = self._generate_default_book_name()

        # Create the book in database
        book_id = self._create_book_in_db(default_name)

        if book_id:
            self.current_book_id = book_id
            self.selected_songs = []

            # Reset all panels
            self.step_panels[1].set_selected_songs([])
            self.step_panels[1].set_book_name(default_name)
            self.step_panels[4].reset()

            # Refresh book list to show new card
            self.book_list.refresh()
            # Select the new book in the list
            self.book_list.select_book_by_id(book_id)

            # Go to step 1
            self._show_step(1)
            self.status_label.configure(text=f"Nouveau book: {default_name}")
        else:
            self._show_warning("Erreur lors de la creation du book")

    def _generate_default_book_name(self) -> str:
        """Generate a default book name like 'Mon Music Book 1', 'Mon Music Book 2', etc."""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

        try:
            from app import app, db
            from models.book import Book

            with app.app_context():
                # Find highest number used
                existing = Book.query.filter(Book.title.like("Mon Music Book%")).all()
                numbers = []
                for book in existing:
                    title = book.title
                    if title == "Mon Music Book":
                        numbers.append(1)
                    elif title.startswith("Mon Music Book "):
                        try:
                            num = int(title.replace("Mon Music Book ", ""))
                            numbers.append(num)
                        except ValueError:
                            pass

                next_num = max(numbers, default=0) + 1
                if next_num == 1:
                    return "Mon Music Book"
                return f"Mon Music Book {next_num}"
        except Exception as e:
            print(f"Erreur generation nom: {e}")
            return "Mon Music Book"

    def _create_book_in_db(self, title: str) -> Optional[int]:
        """Create a new book in the database and return its ID"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

        try:
            from app import app, db
            from models.book import Book

            with app.app_context():
                book = Book(
                    title=title,
                    instrument='guitar',
                    include_cover=True,
                    include_toc=True,
                    include_index=True
                )
                db.session.add(book)
                db.session.commit()
                print(f"Nouveau book cree: {title} (ID: {book.id})")
                return book.id
        except Exception as e:
            print(f"Erreur creation book: {e}")
            return None

    def _on_book_name_change(self, new_name: str):
        """Handle book name change from step 1 - update in DB and refresh card"""
        if not self.current_book_id or not new_name.strip():
            return

        self._update_book_title_in_db(self.current_book_id, new_name)
        # Refresh only the card display
        self.book_list.update_book_title(self.current_book_id, new_name)

    def _update_book_title_in_db(self, book_id: int, new_title: str) -> bool:
        """Update book title in database"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

        try:
            from app import app, db
            from models.book import Book

            with app.app_context():
                book = Book.query.get(book_id)
                if book:
                    book.title = new_title
                    db.session.commit()
                    return True
                return False
        except Exception as e:
            print(f"Erreur mise a jour titre: {e}")
            return False

    def _refresh_book_list(self):
        """Refresh the book list after generation"""
        self.book_list.refresh()

    def _on_book_rename(self, book_id: int, new_title: str):
        """Handle book rename from context menu"""
        # If the renamed book is the current one, update the book name entry
        if self.current_book_id == book_id:
            self.step_panels[1].set_book_name(new_title)

    # =========================================================================
    # UI HELPERS
    # =========================================================================

    def _show_warning(self, message: str):
        """Show warning dialog"""
        from tkinter import messagebox
        messagebox.showwarning("Attention", message)

    def _open_song_manager(self):
        """Ouvrir la fenetre de gestion de la bibliotheque"""
        def on_close():
            # Rafraichir la liste des morceaux apres fermeture
            self.step_panels[1].refresh_songs()

        SongManagerDialog(self, on_close=on_close)


def main():
    """Application entry point"""
    app = MusicBookWorkflowApp()
    app.mainloop()


if __name__ == "__main__":
    main()
