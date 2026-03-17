"""
Song Library Panel - Step 1: Select and order songs for the book
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any, List
import json

from .constants import (
    INSTRUMENT_COLORS_ALT, INSTRUMENT_LABELS,
    SOURCE_LABELS, DEFAULT_INSTRUMENT_COLOR,
)
from .song_library_display import (
    create_recyclable_item, update_widget_content, get_meta_text,
    update_available_display, update_selected_display
)
from .song_library_filters import (
    sort_songs, filter_songs, resolve_option_value, get_add_all_sort_key
)


class SongLibraryPanel(ctk.CTkFrame):
    """Step 1: Song selection with sorting and filtering"""

    SORT_OPTIONS = [
        ("Titre (A-Z)", "title_asc"),
        ("Titre (Z-A)", "title_desc"),
        ("Artiste (A-Z)", "artist_asc"),
        ("Artiste (Z-A)", "artist_desc"),
        ("Genre", "genre"),
        ("Source", "source"),
    ]

    INSTRUMENT_OPTIONS = [
        ("Tous", ""),
        ("Guitare", "guitar"),
        ("Basse", "bass"),
        ("Violon", "violin"),
    ]

    SOURCE_OPTIONS = [
        ("Toutes", ""),
        ("Ultimate Guitar", "ultimate_guitar"),
        ("Songsterr", "songsterr"),
        ("Boite a chansons", "boite_chansons"),
    ]

    def __init__(self, parent, on_next: Callable, get_selected: Callable, on_book_name_change: Callable = None, on_selection_change: Callable = None):
        super().__init__(parent, fg_color="transparent")

        self.on_next = on_next
        self.get_selected = get_selected
        self.on_book_name_change = on_book_name_change  # Callback when book name changes
        self.on_selection_change = on_selection_change  # Callback when selection changes
        self.all_songs: List[Dict[str, Any]] = []
        self._selected_song_ids_list: List[int] = []  # Ordered list for position
        self._selected_song_ids_set: set = set()  # Set for O(1) lookup
        self._songs_by_id: Dict[int, Dict[str, Any]] = {}  # Index for O(1) song lookup

        # Dynamic filter options (populated from data)
        self.genre_options: List[str] = ["Tous"]
        self.artist_options: List[str] = ["Tous"]

        # Widget cache for recycling (avoid recreating widgets)
        self._available_widgets: List[ctk.CTkFrame] = []
        self._selected_widgets: List[ctk.CTkFrame] = []
        self._update_scheduled = False
        self._filtered_songs: List[Dict[str, Any]] = []  # Current filtered songs
        self._widgets_initialized = False  # Track if widget pool is ready

        self._create_widgets()
        # Defer song loading to after UI is fully rendered
        self.after(100, self.refresh_songs)

    @property
    def selected_song_ids(self) -> List[int]:
        """Backward compatible property returning the ordered list"""
        return self._selected_song_ids_list

    @selected_song_ids.setter
    def selected_song_ids(self, value: List[int]):
        """Update both list and set when assigned"""
        self._selected_song_ids_list = value
        self._selected_song_ids_set = set(value)

    def _create_widgets(self):
        """Create panel UI by composing sub-sections."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._create_header()
        self._create_filter_row1()
        self._create_filter_row2()
        self._create_two_column_layout()

    def _create_header(self):
        """Create header row with title, book name, next button."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header, text="Selection des morceaux",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            header, text="Nom du book:", font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(30, 5))

        self.book_name_var = ctk.StringVar(value="Mon Music Book")
        self.book_name_entry = ctk.CTkEntry(
            header, textvariable=self.book_name_var,
            width=250, font=ctk.CTkFont(size=12)
        )
        self.book_name_entry.pack(side="left", padx=(0, 20))
        self.book_name_var.trace("w", self._on_book_name_changed)

        self.next_btn = ctk.CTkButton(
            header, text="Suivant -->", width=120, command=self._on_next_click
        )
        self.next_btn.pack(side="right")

    def _create_filter_row1(self):
        """Create filter row 1: search, sort, instrument, source."""
        filters1 = ctk.CTkFrame(self, fg_color="transparent")
        filters1.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 2))

        ctk.CTkLabel(filters1, text="Recherche:").pack(side="left", padx=(0, 5))
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *args: self._apply_filters())
        ctk.CTkEntry(filters1, textvariable=self.search_var, width=200).pack(side="left", padx=(0, 20))

        ctk.CTkLabel(filters1, text="Trier:").pack(side="left", padx=(0, 5))
        self.sort_var = ctk.StringVar(value="title_asc")
        ctk.CTkOptionMenu(
            filters1, values=[opt[0] for opt in self.SORT_OPTIONS],
            command=lambda c: self._on_option_change(c, self.sort_var, self.SORT_OPTIONS), width=140
        ).pack(side="left", padx=(0, 20))

        ctk.CTkLabel(filters1, text="Instrument:").pack(side="left", padx=(0, 5))
        self.instrument_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(
            filters1, values=[opt[0] for opt in self.INSTRUMENT_OPTIONS],
            command=lambda c: self._on_option_change(c, self.instrument_var, self.INSTRUMENT_OPTIONS), width=100
        ).pack(side="left", padx=(0, 20))

        ctk.CTkLabel(filters1, text="Source:").pack(side="left", padx=(0, 5))
        self.source_var = ctk.StringVar(value="")
        ctk.CTkOptionMenu(
            filters1, values=[opt[0] for opt in self.SOURCE_OPTIONS],
            command=lambda c: self._on_option_change(c, self.source_var, self.SOURCE_OPTIONS), width=140
        ).pack(side="left")

    def _create_filter_row2(self):
        """Create filter row 2: genre, artist."""
        filters2 = ctk.CTkFrame(self, fg_color="transparent")
        filters2.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 10))

        ctk.CTkLabel(filters2, text="Genre:").pack(side="left", padx=(0, 5))
        self.genre_var = ctk.StringVar(value="Tous")
        self.genre_menu = ctk.CTkOptionMenu(
            filters2, values=self.genre_options,
            command=lambda c: self._on_option_change(c, self.genre_var), width=150
        )
        self.genre_menu.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(filters2, text="Artiste:").pack(side="left", padx=(0, 5))
        self.artist_var = ctk.StringVar(value="Tous")
        self.artist_menu = ctk.CTkOptionMenu(
            filters2, values=self.artist_options,
            command=lambda c: self._on_option_change(c, self.artist_var), width=180
        )
        self.artist_menu.pack(side="left")

    def _create_two_column_layout(self):
        """Create the available/selected two-column layout."""
        self._create_available_column()
        self._create_selected_column()

    def _create_available_column(self):
        """Create left column: available songs library."""
        left_frame = ctk.CTkFrame(self, corner_radius=10)
        left_frame.grid(row=3, column=0, sticky="nsew", padx=(20, 10), pady=10)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left_frame, text="Bibliotheque",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))

        self.available_list = ctk.CTkScrollableFrame(left_frame)
        self.available_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        ctk.CTkButton(
            left_frame, text="Ajouter tout ->",
            command=self._add_all_songs, width=120
        ).grid(row=2, column=0, pady=(0, 10))

    def _create_selected_column(self):
        """Create right column: selected songs with order controls."""
        right_frame = ctk.CTkFrame(self, corner_radius=10)
        right_frame.grid(row=3, column=1, sticky="nsew", padx=(10, 20), pady=10)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        right_header = ctk.CTkFrame(right_frame, fg_color="transparent")
        right_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            right_header, text="Morceaux selectionnes",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        self.count_label = ctk.CTkLabel(
            right_header, text="(0)", font=ctk.CTkFont(size=12),
            text_color=("#6b7280", "#9ca3af")
        )
        self.count_label.pack(side="left", padx=5)

        self.selected_list = ctk.CTkScrollableFrame(right_frame)
        self.selected_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        order_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
        order_frame.grid(row=2, column=0, pady=(0, 10))

        ctk.CTkButton(order_frame, text="Haut", width=40, command=self._move_up).pack(side="left", padx=2)
        ctk.CTkButton(order_frame, text="Bas", width=40, command=self._move_down).pack(side="left", padx=2)
        ctk.CTkButton(order_frame, text="Retirer", width=80, command=self._remove_selected,
                      fg_color="#ef4444", hover_color="#dc2626").pack(side="left", padx=10)
        ctk.CTkButton(order_frame, text="Vider tout", width=80, command=self._clear_all,
                      fg_color="#6b7280", hover_color="#4b5563").pack(side="left", padx=2)

    def refresh_songs(self):
        """Load songs from database"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

        try:
            from app import app, db
            from models.song import Song

            with app.app_context():
                songs = Song.query.order_by(Song.title).all()
                self.all_songs = []
                self._songs_by_id = {}  # Rebuild index
                genres_set = set()
                artists_set = set()

                for s in songs:
                    song_data = {
                        'id': s.id,
                        'title': s.title,
                        'artist': s.artist or '',
                        'genre': s.genre or '',
                        'instruments': json.loads(s.instruments) if s.instruments else [],
                        'source': s.source or '',
                        'type': s.type or '',
                        'pages': s.pages or 1,
                        'pdf_path': s.pdf_path
                    }
                    self.all_songs.append(song_data)
                    self._songs_by_id[s.id] = song_data  # Index by ID

                    # Collect unique genres and artists
                    if s.genre:
                        genres_set.add(s.genre)
                    if s.artist:
                        artists_set.add(s.artist)

                # Update filter options
                self.genre_options = ["Tous"] + sorted(genres_set)
                self.artist_options = ["Tous"] + sorted(artists_set)

                # Update menus if they exist
                if hasattr(self, 'genre_menu'):
                    self.genre_menu.configure(values=self.genre_options)
                if hasattr(self, 'artist_menu'):
                    self.artist_menu.configure(values=self.artist_options)

        except Exception as e:
            print(f"Error loading songs: {e}")
            self.all_songs = []

        self._apply_filters()

    def _apply_filters(self):
        """Apply search and filters, then refresh display"""
        filtered = filter_songs(
            self.all_songs,
            search=self.search_var.get().lower(),
            instrument=self.instrument_var.get(),
            source=self.source_var.get(),
            genre=self.genre_var.get() if hasattr(self, 'genre_var') else "Tous",
            artist=self.artist_var.get() if hasattr(self, 'artist_var') else "Tous",
        )
        filtered = sort_songs(filtered, self.sort_var.get())
        self._filtered_songs = filtered
        self._update_available_list(filtered)

    def _on_option_change(self, choice: str, var, options=None):
        """Generic handler for option menu changes.
        If options is a list of (label, value) tuples, maps label->value.
        Otherwise sets choice directly.
        """
        if options:
            for label, value in options:
                if label == choice:
                    var.set(value)
                    break
        else:
            var.set(choice)
        self._apply_filters()

    def _update_available_list(self, songs: List[Dict]):
        """Update the available songs list display using widget recycling"""
        import traceback
        try:
            if not hasattr(self, '_overflow_holder'):
                self._overflow_holder = {}
            update_available_display(
                songs,
                selected_ids_set=self._selected_song_ids_set,
                available_widgets=self._available_widgets,
                available_list=self.available_list,
                add_song_callback=self._add_song,
                overflow_label_holder=self._overflow_holder,
            )
        except Exception as e:
            print(f"ERROR in _update_available_list: {e}")
            traceback.print_exc()

    def _update_selected_list(self):
        """Update the selected songs list display using widget recycling"""
        import traceback
        import time
        try:
            t0, t1, t2 = update_selected_display(
                self._selected_song_ids_list, self._songs_by_id,
                selected_widgets=self._selected_widgets,
                selected_list=self.selected_list,
                count_label=self.count_label,
                on_selection_change=self.on_selection_change,
            )
            # Update available list directly (avoid full _apply_filters)
            self._update_available_list(self._filtered_songs)
            t3 = time.time()
            print(f"_update_selected_list: pool={t1-t0:.3f}s, update_selected={t2-t1:.3f}s, update_available={t3-t2:.3f}s, TOTAL={t3-t0:.3f}s")
        except Exception as e:
            print(f"ERROR in _update_selected_list: {e}")
            traceback.print_exc()

    def _add_song(self, song: Dict):
        """Add a song to selection"""
        song_id = song['id']
        if song_id not in self._selected_song_ids_set:
            self._selected_song_ids_list.append(song_id)
            self._selected_song_ids_set.add(song_id)
            self._update_selected_list()

    def _add_all_songs(self):
        """Add all currently filtered/visible songs to selection, sorted by artist then title"""
        # Get filtered songs not yet selected using O(1) set lookup
        songs_to_add = [s for s in self._filtered_songs if s['id'] not in self._selected_song_ids_set]

        songs_to_add.sort(key=get_add_all_sort_key)

        # Add in sorted order
        for song in songs_to_add:
            song_id = song['id']
            self._selected_song_ids_list.append(song_id)
            self._selected_song_ids_set.add(song_id)

        self._update_selected_list()

    def _remove_selected(self):
        """Remove checked songs from selection"""
        to_remove = []
        for widget in self.selected_list.winfo_children():
            if hasattr(widget, 'check_var') and widget.check_var.get():
                to_remove.append(widget.song_id)

        for song_id in to_remove:
            if song_id in self._selected_song_ids_set:
                self._selected_song_ids_list.remove(song_id)
                self._selected_song_ids_set.discard(song_id)

        self._update_selected_list()

    def _clear_all(self):
        """Clear all selected songs"""
        self._selected_song_ids_list = []
        self._selected_song_ids_set = set()
        self._update_selected_list()

    def _move_up(self):
        """Move checked songs up"""
        for widget in self.selected_list.winfo_children():
            if hasattr(widget, 'check_var') and widget.check_var.get():
                idx = self._selected_song_ids_list.index(widget.song_id)
                if idx > 0:
                    self._selected_song_ids_list[idx], self._selected_song_ids_list[idx-1] = \
                        self._selected_song_ids_list[idx-1], self._selected_song_ids_list[idx]
        self._update_selected_list()

    def _move_down(self):
        """Move checked songs down"""
        widgets = list(self.selected_list.winfo_children())
        for widget in reversed(widgets):
            if hasattr(widget, 'check_var') and widget.check_var.get():
                idx = self._selected_song_ids_list.index(widget.song_id)
                if idx < len(self._selected_song_ids_list) - 1:
                    self._selected_song_ids_list[idx], self._selected_song_ids_list[idx+1] = \
                        self._selected_song_ids_list[idx+1], self._selected_song_ids_list[idx]
        self._update_selected_list()

    def _on_next_click(self):
        """Handle next button click"""
        if not self.selected_song_ids:
            # Show warning
            return
        self.on_next()

    def get_selected_songs(self) -> List[int]:
        """Get list of selected song IDs in order"""
        return self._selected_song_ids_list.copy()

    def set_selected_songs(self, song_ids: List[int]):
        """Set selected songs (for loading existing book)"""
        self._selected_song_ids_list = song_ids.copy()
        self._selected_song_ids_set = set(song_ids)
        self._update_selected_list()

    def get_book_name(self) -> str:
        """Get the current book name"""
        return self.book_name_var.get()

    def set_book_name(self, name: str):
        """Set the book name (without triggering callback)"""
        self._ignore_name_callback = True
        self.book_name_var.set(name)
        self._ignore_name_callback = False

    def _on_book_name_changed(self, *args):
        """Called when book name is modified (debounced)"""
        # Skip if we're programmatically setting the name
        if getattr(self, '_ignore_name_callback', False):
            return

        # Cancel any pending update
        if hasattr(self, '_name_update_id') and self._name_update_id:
            self.after_cancel(self._name_update_id)

        # Schedule update after 500ms of no typing
        self._name_update_id = self.after(500, self._do_book_name_update)

    def _do_book_name_update(self):
        """Execute the debounced book name update"""
        self._name_update_id = None
        if self.on_book_name_change:
            self.on_book_name_change(self.book_name_var.get())
