"""
Song Library Panel - Step 1: Select and order songs for the book
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any, List
import json


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
        """Create panel UI"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)  # Content row expands (row 3 after 2 filter rows)

        # === Header (row 0) ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=20, pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="Selection des morceaux",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        # Book name field
        ctk.CTkLabel(
            header,
            text="Nom du book:",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(30, 5))

        self.book_name_var = ctk.StringVar(value="Mon Music Book")
        self.book_name_entry = ctk.CTkEntry(
            header,
            textvariable=self.book_name_var,
            width=250,
            font=ctk.CTkFont(size=12)
        )
        self.book_name_entry.pack(side="left", padx=(0, 20))
        self.book_name_var.trace("w", self._on_book_name_changed)

        # Next button
        self.next_btn = ctk.CTkButton(
            header,
            text="Suivant -->",
            width=120,
            command=self._on_next_click
        )
        self.next_btn.pack(side="right")

        # === Filters Row 1 (row 1) - Search + Sort ===
        filters1 = ctk.CTkFrame(self, fg_color="transparent")
        filters1.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(5, 2))

        # Search
        ctk.CTkLabel(filters1, text="Recherche:").pack(side="left", padx=(0, 5))
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *args: self._apply_filters())
        ctk.CTkEntry(filters1, textvariable=self.search_var, width=200).pack(side="left", padx=(0, 20))

        # Sort
        ctk.CTkLabel(filters1, text="Trier:").pack(side="left", padx=(0, 5))
        self.sort_var = ctk.StringVar(value="title_asc")
        sort_menu = ctk.CTkOptionMenu(
            filters1,
            values=[opt[0] for opt in self.SORT_OPTIONS],
            command=self._on_sort_change,
            width=140
        )
        sort_menu.pack(side="left", padx=(0, 20))

        # Instrument filter
        ctk.CTkLabel(filters1, text="Instrument:").pack(side="left", padx=(0, 5))
        self.instrument_var = ctk.StringVar(value="")
        inst_menu = ctk.CTkOptionMenu(
            filters1,
            values=[opt[0] for opt in self.INSTRUMENT_OPTIONS],
            command=self._on_instrument_change,
            width=100
        )
        inst_menu.pack(side="left", padx=(0, 20))

        # Source filter
        ctk.CTkLabel(filters1, text="Source:").pack(side="left", padx=(0, 5))
        self.source_var = ctk.StringVar(value="")
        source_menu = ctk.CTkOptionMenu(
            filters1,
            values=[opt[0] for opt in self.SOURCE_OPTIONS],
            command=self._on_source_change,
            width=140
        )
        source_menu.pack(side="left")

        # === Filters Row 2 (row 1.5) - Genre + Artist ===
        filters2 = ctk.CTkFrame(self, fg_color="transparent")
        filters2.grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=(2, 10))

        # Genre filter
        ctk.CTkLabel(filters2, text="Genre:").pack(side="left", padx=(0, 5))
        self.genre_var = ctk.StringVar(value="Tous")
        self.genre_menu = ctk.CTkOptionMenu(
            filters2,
            values=self.genre_options,
            command=self._on_genre_change,
            width=150
        )
        self.genre_menu.pack(side="left", padx=(0, 20))

        # Artist filter
        ctk.CTkLabel(filters2, text="Artiste:").pack(side="left", padx=(0, 5))
        self.artist_var = ctk.StringVar(value="Tous")
        self.artist_menu = ctk.CTkOptionMenu(
            filters2,
            values=self.artist_options,
            command=self._on_artist_change,
            width=180
        )
        self.artist_menu.pack(side="left")

        # === Two columns: Available / Selected (row 3) ===

        # Left: Available songs
        left_frame = ctk.CTkFrame(self, corner_radius=10)
        left_frame.grid(row=3, column=0, sticky="nsew", padx=(20, 10), pady=10)
        left_frame.grid_rowconfigure(1, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            left_frame,
            text="Bibliothèque",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))

        self.available_list = ctk.CTkScrollableFrame(left_frame)
        self.available_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Add all button
        ctk.CTkButton(
            left_frame,
            text="Ajouter tout ->",
            command=self._add_all_songs,
            width=120
        ).grid(row=2, column=0, pady=(0, 10))

        # Right: Selected songs
        right_frame = ctk.CTkFrame(self, corner_radius=10)
        right_frame.grid(row=3, column=1, sticky="nsew", padx=(10, 20), pady=10)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # Header with count
        right_header = ctk.CTkFrame(right_frame, fg_color="transparent")
        right_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))

        ctk.CTkLabel(
            right_header,
            text="Morceaux sélectionnés",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="left")

        self.count_label = ctk.CTkLabel(
            right_header,
            text="(0)",
            font=ctk.CTkFont(size=12),
            text_color=("#6b7280", "#9ca3af")
        )
        self.count_label.pack(side="left", padx=5)

        self.selected_list = ctk.CTkScrollableFrame(right_frame)
        self.selected_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Order buttons
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
        search = self.search_var.get().lower()
        instrument = self.instrument_var.get()
        source = self.source_var.get()
        genre = self.genre_var.get() if hasattr(self, 'genre_var') else "Tous"
        artist = self.artist_var.get() if hasattr(self, 'artist_var') else "Tous"

        filtered = []
        for song in self.all_songs:
            # Search filter
            if search:
                if search not in song['title'].lower() and search not in song['artist'].lower():
                    continue

            # Instrument filter
            if instrument and instrument not in song['instruments']:
                continue

            # Source filter
            if source and song['source'] != source:
                continue

            # Genre filter
            if genre and genre != "Tous" and song['genre'] != genre:
                continue

            # Artist filter
            if artist and artist != "Tous" and song['artist'] != artist:
                continue

            filtered.append(song)

        # Apply sorting
        sort_key = self.sort_var.get()
        filtered = self._sort_songs(filtered, sort_key)

        # Store filtered songs for "Add all" functionality
        self._filtered_songs = filtered

        # Update available list
        self._update_available_list(filtered)

    def _sort_songs(self, songs: List[Dict], sort_key: str) -> List[Dict]:
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

    def _on_sort_change(self, choice: str):
        """Handle sort option change"""
        for label, value in self.SORT_OPTIONS:
            if label == choice:
                self.sort_var.set(value)
                break
        self._apply_filters()

    def _on_instrument_change(self, choice: str):
        """Handle instrument filter change"""
        for label, value in self.INSTRUMENT_OPTIONS:
            if label == choice:
                self.instrument_var.set(value)
                break
        self._apply_filters()

    def _on_source_change(self, choice: str):
        """Handle source filter change"""
        for label, value in self.SOURCE_OPTIONS:
            if label == choice:
                self.source_var.set(value)
                break
        self._apply_filters()

    def _on_genre_change(self, choice: str):
        """Handle genre filter change"""
        self.genre_var.set(choice)
        self._apply_filters()

    def _on_artist_change(self, choice: str):
        """Handle artist filter change"""
        self.artist_var.set(choice)
        self._apply_filters()

    def _update_available_list(self, songs: List[Dict]):
        """Update the available songs list display using widget recycling"""
        import traceback
        import time
        try:
            t0 = time.time()

            # Filter out already selected songs using set for O(1) lookup
            available = [s for s in songs if s['id'] not in self._selected_song_ids_set]

            MAX_DISPLAY = 50
            songs_to_show = available[:MAX_DISPLAY]
            num_to_show = len(songs_to_show)

            # Ensure we have enough widgets in the pool
            while len(self._available_widgets) < num_to_show:
                widget = self._create_recyclable_item(self.available_list, is_available=True)
                self._available_widgets.append(widget)

            t1 = time.time()

            # Update visible widgets with new data
            for i, song in enumerate(songs_to_show):
                widget = self._available_widgets[i]
                self._update_widget_content(widget, song, is_available=True)
                widget.pack(fill="x", pady=2, padx=2)

            # Hide unused widgets
            for i in range(num_to_show, len(self._available_widgets)):
                self._available_widgets[i].pack_forget()

            t2 = time.time()

            # Handle overflow label
            if not hasattr(self, '_available_overflow_label'):
                self._available_overflow_label = ctk.CTkLabel(
                    self.available_list,
                    text="",
                    font=ctk.CTkFont(size=11),
                    text_color=("#6b7280", "#9ca3af")
                )

            if len(available) > MAX_DISPLAY:
                self._available_overflow_label.configure(text=f"... et {len(available) - MAX_DISPLAY} autres")
                self._available_overflow_label.pack(pady=10)
            else:
                self._available_overflow_label.pack_forget()

            print(f"⏱️ _update_available_list: pool={t1-t0:.3f}s, update={t2-t1:.3f}s, TOTAL={t2-t0:.3f}s (showing {num_to_show}/{len(available)})")
        except Exception as e:
            print(f"ERROR in _update_available_list: {e}")
            traceback.print_exc()

    def _update_selected_list(self):
        """Update the selected songs list display using widget recycling"""
        import traceback
        import time
        try:
            t0 = time.time()

            num_selected = len(self._selected_song_ids_list)

            # Ensure we have enough widgets in the pool
            while len(self._selected_widgets) < num_selected:
                widget = self._create_recyclable_item(self.selected_list, is_available=False)
                self._selected_widgets.append(widget)

            t1 = time.time()

            # Update visible widgets with new data
            for i, song_id in enumerate(self._selected_song_ids_list):
                song = self._songs_by_id.get(song_id)
                if song:
                    widget = self._selected_widgets[i]
                    self._update_widget_content(widget, song, is_available=False, position=i+1)
                    widget.pack(fill="x", pady=2, padx=2)

            # Hide unused widgets
            for i in range(num_selected, len(self._selected_widgets)):
                self._selected_widgets[i].pack_forget()

            t2 = time.time()

            # Update count
            self.count_label.configure(text=f"({num_selected})")

            # Notify parent of selection change
            if self.on_selection_change:
                self.on_selection_change()

            # Update available list directly (avoid full _apply_filters)
            self._update_available_list(self._filtered_songs)
            t3 = time.time()

            print(f"⏱️ _update_selected_list: pool={t1-t0:.3f}s, update_selected={t2-t1:.3f}s, update_available={t3-t2:.3f}s, TOTAL={t3-t0:.3f}s")
        except Exception as e:
            print(f"ERROR in _update_selected_list: {e}")
            traceback.print_exc()

    def _create_recyclable_item(self, parent, is_available: bool) -> ctk.CTkFrame:
        """Create a reusable song item widget (created once, updated many times)"""
        item = ctk.CTkFrame(parent, corner_radius=4, fg_color=("#f9fafb", "#1f2937"), height=36)

        # Single line layout - more compact and faster
        # Position label (for selected list)
        pos_label = ctk.CTkLabel(item, text="", width=25, anchor="e")
        pos_label.pack(side="left", padx=(8, 4))
        item._pos_label = pos_label

        # Title label (main info)
        title_label = ctk.CTkLabel(item, text="", anchor="w")
        title_label.pack(side="left", fill="x", expand=True, padx=4)
        item._title_label = title_label

        # Button or checkbox
        if is_available:
            btn = ctk.CTkButton(item, text="+", width=28, height=24, corner_radius=4)
            btn.pack(side="right", padx=6, pady=4)
            item._action_btn = btn
            item._check_var = None
        else:
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(item, text="", variable=var, width=20, height=20)
            cb.pack(side="right", padx=6)
            item._action_btn = None
            item._check_var = var
            item.check_var = var

        item._is_available = is_available
        return item

    def _update_widget_content(self, widget: ctk.CTkFrame, song: Dict, is_available: bool, position: int = None):
        """Update the content of a recyclable widget"""
        # Update position (compact format)
        if position:
            widget._pos_label.configure(text=f"{position}.")
        else:
            widget._pos_label.configure(text="")

        # Compact title with artist
        artist = song.get('artist', '')
        title = song['title']
        if artist:
            display_text = f"{title} - {artist}"
        else:
            display_text = title
        widget._title_label.configure(text=display_text)

        # Update action button command or song_id
        if is_available and widget._action_btn:
            widget._action_btn.configure(command=lambda s=song: self._add_song(s))
        elif not is_available:
            widget.song_id = song['id']
            if widget._check_var:
                widget._check_var.set(False)

    def _create_song_item(self, parent, song: Dict, is_available: bool, position: int = None):
        """Create a song list item and return it for caching"""
        import traceback
        try:
            item = ctk.CTkFrame(parent, corner_radius=6, fg_color=("#f9fafb", "#1f2937"))
            item.pack(fill="x", pady=2, padx=2)

            content = ctk.CTkFrame(item, fg_color="transparent")
            content.pack(fill="x", padx=10, pady=6)

            # Position label (for selected list)
            if position:
                pos_label = ctk.CTkLabel(
                    content,
                    text=f"{position}.",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    width=25
                )
                pos_label.pack(side="left")

            # Badge container for instruments
            badge_frame = ctk.CTkFrame(content, fg_color="transparent")
            badge_frame.pack(side="left")

            # Create badges - inline to avoid issues
            instruments = song.get('instruments', [])
            inst_colors = {
                'guitar': ("#22c55e", "#16a34a"),
                'bass': ("#f59e0b", "#d97706"),
                'violin': ("#8b5cf6", "#7c3aed"),
                'piano': ("#3b82f6", "#2563eb"),
                'ukulele': ("#ec4899", "#db2777")
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
                    badge_frame,
                    text=label,
                    font=ctk.CTkFont(size=9, weight="bold"),
                    fg_color=color,
                    text_color="white",
                    corner_radius=4,
                    width=35,
                    height=18
                )
                badge.pack(side="left", padx=(0, 8))

            # Song info
            info_frame = ctk.CTkFrame(content, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True)

            # Title
            title_label = ctk.CTkLabel(
                info_frame,
                text=song['title'],
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            title_label.pack(fill="x")

            # Meta info
            meta_text = self._get_meta_text(song)
            meta_label = ctk.CTkLabel(
                info_frame,
                text=meta_text,
                font=ctk.CTkFont(size=10),
                text_color=("#6b7280", "#9ca3af"),
                anchor="w"
            )
            meta_label.pack(fill="x")

            # Add/Remove button or checkbox
            if is_available:
                btn = ctk.CTkButton(
                    content,
                    text="+",
                    width=30,
                    height=30,
                    command=lambda s=song: self._add_song(s)
                )
                btn.pack(side="right")
            else:
                var = ctk.BooleanVar(value=False)
                cb = ctk.CTkCheckBox(content, text="", variable=var, width=20)
                cb.pack(side="right")
                item.check_var = var
                item.song_id = song['id']
        except Exception as e:
            print(f"ERROR in _create_song_item: {e}")
            traceback.print_exc()

    def _update_badges(self, badge_frame, instruments: List[str]):
        """Update instrument badges in a frame"""
        # Clear existing badges
        for w in badge_frame.winfo_children():
            w.destroy()

        if not instruments:
            return

        inst_colors = {
            'guitar': ("#22c55e", "#16a34a"),
            'bass': ("#f59e0b", "#d97706"),
            'violin': ("#8b5cf6", "#7c3aed"),
            'piano': ("#3b82f6", "#2563eb"),
            'ukulele': ("#ec4899", "#db2777")
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
                badge_frame,
                text=label,
                font=ctk.CTkFont(size=9, weight="bold"),
                fg_color=color,
                text_color="white",
                corner_radius=4,
                width=35,
                height=18
            )
            badge.pack(side="left", padx=(0, 8))

    def _get_meta_text(self, song: Dict) -> str:
        """Build meta text for a song"""
        meta_parts = [song['artist']] if song.get('artist') else []
        if song.get('source'):
            source_display = {
                'ultimate_guitar': 'UG',
                'songsterr': 'SS',
                'boite_chansons': 'BAC'
            }.get(song['source'], song['source'])
            meta_parts.append(source_display)
        return ' | '.join(meta_parts)

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

        # Sort by artist LAST NAME (last word), then by title
        # Ex: "Georges Brassens" -> sort on "Brassens"
        # Ex: "Renaud" -> sort on "Renaud"
        def get_sort_key(song):
            artist = song.get('artist', '').strip()
            if artist:
                # Use last word as surname
                surname = artist.split()[-1].lower()
            else:
                surname = ''
            title = song.get('title', '').lower()
            return (surname, title)

        songs_to_add.sort(key=get_sort_key)

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
