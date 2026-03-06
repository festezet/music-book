"""
Book List Panel - Shows existing books and allows creating new ones
"""
import customtkinter as ctk
from typing import Callable, Optional, Dict, Any, List
from datetime import datetime
from tkinter import Menu, messagebox, simpledialog


class BookListPanel(ctk.CTkFrame):
    """Panel showing list of books (saved and in-progress)"""

    def __init__(self, parent, on_select: Callable, on_new: Callable, on_rename: Callable = None, width: int = 250):
        super().__init__(parent, width=width, corner_radius=10)

        self.on_select = on_select
        self.on_new = on_new
        self.on_rename = on_rename  # Callback when book is renamed (book_id, new_title)
        self.books: List[Dict[str, Any]] = []

        # Context menu
        self.context_menu = None
        self._selected_book_for_menu: Optional[Dict[str, Any]] = None

        # Track selected book for highlighting
        self._selected_book_id: Optional[int] = None
        self._book_frames: Dict[int, ctk.CTkFrame] = {}
        self._book_info_labels: Dict[int, ctk.CTkLabel] = {}  # For updating song count

        self._create_widgets()
        self._create_context_menu()
        # Defer loading to after UI is rendered
        self.after(50, self.refresh)

    def _create_widgets(self):
        """Create panel UI"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(
            header_frame,
            text=" Mes Books",
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w"
        ).pack(side="left")

        # New book button
        ctk.CTkButton(
            header_frame,
            text="+ Nouveau",
            width=80,
            height=28,
            font=ctk.CTkFont(size=12),
            command=self.on_new
        ).pack(side="right")

        # Separator
        ctk.CTkFrame(self, height=2, fg_color=("#e5e7eb", "#374151")).pack(
            fill="x", padx=15, pady=(0, 10)
        )

        # Scrollable list
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.list_frame,
            text="Aucun book\nCliquez sur '+ Nouveau'",
            font=ctk.CTkFont(size=12),
            text_color=("#9ca3af", "#6b7280"),
            justify="center"
        )

    def refresh(self):
        """Refresh the book list from database"""
        # Clear existing items and frame references
        self._book_frames.clear()
        self._book_info_labels.clear()
        for widget in self.list_frame.winfo_children():
            if widget != self.empty_label:
                widget.destroy()

        # Load books from database
        self._load_books()

        if not self.books:
            self.empty_label.pack(pady=30)
        else:
            self.empty_label.pack_forget()
            for book in self.books:
                self._create_book_item(book)

    def _load_books(self):
        """Load books from database"""
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

        try:
            from app import app, db
            from models.book import Book

            with app.app_context():
                books = Book.query.order_by(Book.created_at.desc()).all()
                self.books = [b.to_dict() for b in books]
        except Exception as e:
            print(f"Error loading books: {e}")
            self.books = []

    def _create_book_item(self, book: Dict[str, Any]):
        """Create a book list item"""
        book_id = book['id']
        is_selected = self._selected_book_id == book_id

        # Different colors for selected vs normal
        if is_selected:
            fg_color = ("#3b82f6", "#2563eb")  # Blue for selected
        else:
            fg_color = ("#f3f4f6", "#374151")  # Default gray

        item = ctk.CTkFrame(self.list_frame, corner_radius=8, fg_color=fg_color)
        item.pack(fill="x", padx=5, pady=3)

        # Store reference for highlighting
        self._book_frames[book_id] = item

        # Make clickable (left click = select, right click = context menu)
        item.bind("<Button-1>", lambda e, b=book: self._select_book(b))
        item.bind("<Button-3>", lambda e, b=book: self._show_context_menu(e, b))

        # Content
        content = ctk.CTkFrame(item, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)
        content.bind("<Button-1>", lambda e, b=book: self._select_book(b))
        content.bind("<Button-3>", lambda e, b=book: self._show_context_menu(e, b))

        # Text color based on selection
        text_color = ("white", "white") if is_selected else None
        sub_text_color = ("#e5e7eb", "#d1d5db") if is_selected else ("#6b7280", "#9ca3af")

        # Title
        title_label = ctk.CTkLabel(
            content,
            text=book.get('title', 'Sans titre'),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=text_color,
            anchor="w"
        )
        title_label.pack(fill="x")
        title_label.bind("<Button-1>", lambda e, b=book: self._select_book(b))
        title_label.bind("<Button-3>", lambda e, b=book: self._show_context_menu(e, b))

        # Info line (instrument + morceaux)
        instrument = book.get('instrument', 'guitar')
        song_count = book.get('song_count', 0)
        # Instrument icon without emoji for CTk compatibility
        inst_display = {'guitar': 'Guitare', 'bass': 'Basse', 'violin': 'Violon'}.get(instrument, instrument.capitalize())
        info_text = f"{inst_display} - {song_count} morceaux"

        info_label = ctk.CTkLabel(
            content,
            text=info_text,
            font=ctk.CTkFont(size=11),
            text_color=sub_text_color,
            anchor="w"
        )
        info_label.pack(fill="x")
        info_label.bind("<Button-1>", lambda e, b=book: self._select_book(b))
        info_label.bind("<Button-3>", lambda e, b=book: self._show_context_menu(e, b))

        # Store reference for updating song count
        self._book_info_labels[book_id] = info_label
        info_label._instrument = instrument  # Store for rebuilding text

        # Date line
        created_at = book.get('created_at', '')
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at)
                date_text = dt.strftime('%d/%m/%Y %H:%M')
            except:
                date_text = ""
        else:
            date_text = ""

        if date_text:
            date_label = ctk.CTkLabel(
                content,
                text=date_text,
                font=ctk.CTkFont(size=10),
                text_color=sub_text_color,
                anchor="w"
            )
            date_label.pack(fill="x")
            date_label.bind("<Button-1>", lambda e, b=book: self._select_book(b))
            date_label.bind("<Button-3>", lambda e, b=book: self._show_context_menu(e, b))

    def add_current_book(self, title: str, song_count: int):
        """Add current working book to display"""
        # This is for showing the in-progress book
        pass

    def _select_book(self, book: Dict[str, Any]):
        """Handle book selection with highlighting"""
        import time
        import traceback
        t0 = time.time()

        try:
            book_id = book['id']
            print(f"🔵 _select_book called: book_id={book_id}, current={self._selected_book_id}")
            old_selected_id = self._selected_book_id

            # Update selected book ID
            self._selected_book_id = book_id

            # Update highlighting without full refresh - just change colors
            self._update_highlight(old_selected_id, book_id)
            t1 = time.time()

            # Call the parent's on_select callback
            self.on_select(book_id, book)
            t2 = time.time()

            print(f"⏱️ _select_book: highlight={t1-t0:.3f}s, on_select_callback={t2-t1:.3f}s, TOTAL={t2-t0:.3f}s")
        except Exception as e:
            print(f"❌ ERROR in _select_book: {e}")
            traceback.print_exc()

    def _update_highlight(self, old_id: Optional[int], new_id: int):
        """Update highlighting colors without recreating widgets"""
        # Skip if selecting the same book
        if old_id == new_id:
            return

        print(f"🎨 _update_highlight: old={old_id}, new={new_id}, frames={list(self._book_frames.keys())}")

        # Remove highlight from old selection
        if old_id and old_id in self._book_frames:
            old_frame = self._book_frames[old_id]
            old_frame.configure(fg_color=("#f3f4f6", "#374151"))
            self._update_frame_text_colors(old_frame, is_selected=False)
            print(f"   ✓ Old frame {old_id} updated to gray")

        # Add highlight to new selection
        if new_id in self._book_frames:
            new_frame = self._book_frames[new_id]
            new_frame.configure(fg_color=("#3b82f6", "#2563eb"))
            self._update_frame_text_colors(new_frame, is_selected=True)
            print(f"   ✓ New frame {new_id} updated to blue")

    def _update_frame_text_colors(self, frame: ctk.CTkFrame, is_selected: bool):
        """Update text colors for all labels in a frame"""
        # Default text colors for CTk in light/dark mode (cannot use None)
        title_color = ("white", "white") if is_selected else ("#1a1a1a", "#dce4ee")
        sub_color = ("#e5e7eb", "#d1d5db") if is_selected else ("#6b7280", "#9ca3af")

        for child in frame.winfo_children():
            if isinstance(child, ctk.CTkFrame):
                first_label = True
                for label in child.winfo_children():
                    if isinstance(label, ctk.CTkLabel):
                        if first_label:
                            label.configure(text_color=title_color)
                            first_label = False
                        else:
                            label.configure(text_color=sub_color)

    def set_selected(self, book_id: Optional[int]):
        """Set the selected book (for external control)"""
        self._selected_book_id = book_id
        self.refresh()

    def update_song_count(self, book_id: int, count: int):
        """Update the song count displayed on a book card"""
        if book_id in self._book_info_labels:
            label = self._book_info_labels[book_id]
            instrument = getattr(label, '_instrument', 'guitar')
            inst_display = {'guitar': 'Guitare', 'bass': 'Basse', 'violin': 'Violon'}.get(
                instrument, instrument.capitalize())
            label.configure(text=f"{inst_display} - {count} morceaux")

    def _create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = Menu(self, tearoff=0, bg="#2b2b2b", fg="white",
                                  activebackground="#3b82f6", activeforeground="white")
        self.context_menu.add_command(
            label="Renommer",
            command=self._rename_selected_book
        )
        self.context_menu.add_separator()
        self.context_menu.add_command(
            label="Supprimer ce book",
            command=self._delete_selected_book
        )

    def _show_context_menu(self, event, book: Dict[str, Any]):
        """Show context menu on right-click"""
        self._selected_book_for_menu = book
        # Post the menu at cursor position
        self.context_menu.post(event.x_root, event.y_root)
        # Bind click anywhere to close the menu
        self.context_menu.bind("<FocusOut>", lambda e: self.context_menu.unpost())

    def _delete_selected_book(self):
        """Delete the selected book after confirmation"""
        if not self._selected_book_for_menu:
            return

        book = self._selected_book_for_menu
        title = book.get('title', 'Sans titre')

        # Confirmation dialog
        if not messagebox.askyesno(
            "Confirmer la suppression",
            f"Supprimer le book '{title}' ?\n\nCette action est irreversible."
        ):
            return

        # Delete from database
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

        try:
            from app import app, db
            from models.book import Book
            from models.book_song import BookSong

            with app.app_context():
                # Delete associated book_songs first
                BookSong.query.filter_by(book_id=book['id']).delete()
                # Delete the book
                Book.query.filter_by(id=book['id']).delete()
                db.session.commit()

            messagebox.showinfo("Succes", f"Book '{title}' supprime.")
            self.refresh()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression:\n{e}")

        self._selected_book_for_menu = None

    def _rename_selected_book(self):
        """Rename the selected book via dialog"""
        if not self._selected_book_for_menu:
            return

        book = self._selected_book_for_menu
        current_title = book.get('title', 'Sans titre')

        # Show input dialog
        new_title = simpledialog.askstring(
            "Renommer le book",
            "Nouveau nom:",
            initialvalue=current_title,
            parent=self
        )

        if not new_title or new_title.strip() == "" or new_title == current_title:
            self._selected_book_for_menu = None
            return

        new_title = new_title.strip()

        # Update in database
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

        try:
            from app import app, db
            from models.book import Book

            with app.app_context():
                db_book = Book.query.get(book['id'])
                if db_book:
                    db_book.title = new_title
                    db.session.commit()

            # Update display without full refresh
            self.update_book_title(book['id'], new_title)

            # Notify parent app if callback provided
            if self.on_rename:
                self.on_rename(book['id'], new_title)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du renommage:\n{e}")

        self._selected_book_for_menu = None

    def select_book_by_id(self, book_id: int):
        """Select a book by its ID (used after creating a new book)"""
        self._selected_book_id = book_id
        # Find the book in our list and trigger visual update
        for book in self.books:
            if book['id'] == book_id:
                # Update highlighting without calling on_select (to avoid loop)
                self.refresh()
                break

    def update_book_title(self, book_id: int, new_title: str):
        """Update the title display of a book card dynamically (without full refresh)"""
        if book_id in self._book_frames:
            frame = self._book_frames[book_id]
            # Find the content frame and title label
            for child in frame.winfo_children():
                if isinstance(child, ctk.CTkFrame):  # content frame
                    for subchild in child.winfo_children():
                        if isinstance(subchild, ctk.CTkLabel):
                            # First label is the title
                            subchild.configure(text=new_title)
                            # Also update our internal data
                            for book in self.books:
                                if book['id'] == book_id:
                                    book['title'] = new_title
                                    break
                            return
