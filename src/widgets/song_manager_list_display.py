"""
Song Manager List Display - Song item creation and display helpers.
Extracted from song_manager.py for modularity.
"""
import customtkinter as ctk
import os
from tkinter import messagebox
from typing import Dict, Callable

from .constants import (
    INSTRUMENT_COLORS, INSTRUMENT_LABELS, DEFAULT_INSTRUMENT_COLOR
)


def create_song_item(parent, song: Dict, is_selected: bool,
                     on_select: Callable, on_context_menu: Callable):
    """Create a song list item widget with badges and info labels."""
    fg_color = ("#3b82f6", "#2563eb") if is_selected else ("#f3f4f6", "#374151")

    item = ctk.CTkFrame(parent, corner_radius=6, fg_color=fg_color, height=50)
    item.pack(fill="x", pady=2, padx=2, expand=True)

    content = ctk.CTkFrame(item, fg_color="transparent")
    content.pack(fill="x", padx=10, pady=8)

    for w in (item, content):
        w.bind("<Button-1>", lambda e, s=song: on_select(s))
        w.bind("<Button-3>", lambda e, s=song: on_context_menu(e, s))

    _add_instrument_badges(content, song, on_select, on_context_menu)
    _add_song_info_labels(content, song, is_selected, on_select, on_context_menu)


def _add_instrument_badges(parent, song: Dict, on_select: Callable, on_context_menu: Callable):
    """Add colored instrument badges to a song item."""
    instruments = song.get('instruments') or []
    for inst in instruments:
        color = INSTRUMENT_COLORS.get(inst, DEFAULT_INSTRUMENT_COLOR)
        label = INSTRUMENT_LABELS.get(inst, inst[:3].upper())
        badge = ctk.CTkLabel(
            parent, text=label,
            font=ctk.CTkFont(size=9, weight="bold"),
            fg_color=color, text_color="white",
            corner_radius=4, width=35, height=18
        )
        badge.pack(side="left", padx=(0, 8))
        badge.bind("<Button-1>", lambda e, s=song: on_select(s))
        badge.bind("<Button-3>", lambda e, s=song: on_context_menu(e, s))


def _add_song_info_labels(parent, song: Dict, is_selected: bool,
                          on_select: Callable, on_context_menu: Callable):
    """Add title and meta labels to a song item."""
    text_color = ("white", "white") if is_selected else None
    sub_color = ("#e5e7eb", "#d1d5db") if is_selected else ("#6b7280", "#9ca3af")

    info_frame = ctk.CTkFrame(parent, fg_color="transparent")
    info_frame.pack(side="left", fill="x", expand=True)

    title_label = ctk.CTkLabel(
        info_frame, text=song['title'],
        font=ctk.CTkFont(size=12, weight="bold"),
        text_color=text_color, anchor="w"
    )
    title_label.pack(fill="x")

    meta_parts = []
    if song.get('artist'):
        meta_parts.append(song['artist'])
    if song.get('genre'):
        meta_parts.append(song['genre'])
    meta_text = " - ".join(meta_parts) if meta_parts else "Sans artiste"

    meta_label = ctk.CTkLabel(
        info_frame, text=meta_text,
        font=ctk.CTkFont(size=10), text_color=sub_color, anchor="w"
    )
    meta_label.pack(fill="x")

    for w in (info_frame, title_label, meta_label):
        w.bind("<Button-1>", lambda e, s=song: on_select(s))
        w.bind("<Button-3>", lambda e, s=song: on_context_menu(e, s))


def open_pdf(song: Dict):
    """Open the PDF file for a song."""
    pdf_path = song.get('pdf_path')
    if pdf_path and os.path.exists(pdf_path):
        import subprocess
        subprocess.run(['xdg-open', pdf_path], check=False)
    else:
        messagebox.showwarning("Attention", f"Fichier PDF introuvable:\n{pdf_path}")


def open_folder(song: Dict):
    """Open the folder containing the song's PDF."""
    pdf_path = song.get('pdf_path')
    if pdf_path:
        folder = os.path.dirname(pdf_path)
        if os.path.exists(folder):
            import subprocess
            subprocess.run(['xdg-open', folder], check=False)
        else:
            messagebox.showwarning("Attention", f"Dossier introuvable:\n{folder}")
