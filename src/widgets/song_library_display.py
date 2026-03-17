"""
Song Library Display Helpers - Widget recycling and display logic.
Extracted from song_library.py for modularity.
"""
import customtkinter as ctk
from typing import Dict, List, Callable

from .constants import SOURCE_LABELS


def create_recyclable_item(parent, is_available: bool, add_song_callback: Callable = None) -> ctk.CTkFrame:
    """Create a reusable song item widget (created once, updated many times)"""
    item = ctk.CTkFrame(parent, corner_radius=4, fg_color=("#f9fafb", "#1f2937"), height=36)

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


def update_widget_content(widget: ctk.CTkFrame, song: Dict, is_available: bool,
                          add_song_callback: Callable = None, position: int = None):
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
        widget._action_btn.configure(command=lambda s=song: add_song_callback(s))
    elif not is_available:
        widget.song_id = song['id']
        if widget._check_var:
            widget._check_var.set(False)


def get_meta_text(song: Dict) -> str:
    """Build meta text for a song"""
    meta_parts = [song['artist']] if song.get('artist') else []
    if song.get('source'):
        meta_parts.append(SOURCE_LABELS.get(song['source'], song['source']))
    return ' | '.join(meta_parts)


def update_available_display(songs: List[Dict], **ctx):
    """Update the available songs list display using widget recycling.

    Keyword args:
        selected_ids_set: Set of selected song IDs for O(1) lookup.
        available_widgets: Pool of recyclable widgets (modified in-place).
        available_list: Parent scrollable frame.
        add_song_callback: Callback to add a song.
        overflow_label_holder: Dict with key '_available_overflow_label' (created if missing).
    """
    selected_ids_set = ctx['selected_ids_set']
    available_widgets = ctx['available_widgets']
    available_list = ctx['available_list']
    add_song_callback = ctx['add_song_callback']
    overflow_label_holder = ctx['overflow_label_holder']
    import time
    t0 = time.time()

    # Filter out already selected songs using set for O(1) lookup
    available = [s for s in songs if s['id'] not in selected_ids_set]

    MAX_DISPLAY = 50
    songs_to_show = available[:MAX_DISPLAY]
    num_to_show = len(songs_to_show)

    # Ensure we have enough widgets in the pool
    while len(available_widgets) < num_to_show:
        widget = create_recyclable_item(available_list, is_available=True)
        available_widgets.append(widget)

    t1 = time.time()

    # Update visible widgets with new data
    for i, song in enumerate(songs_to_show):
        widget = available_widgets[i]
        update_widget_content(widget, song, is_available=True, add_song_callback=add_song_callback)
        widget.pack(fill="x", pady=2, padx=2)

    # Hide unused widgets
    for i in range(num_to_show, len(available_widgets)):
        available_widgets[i].pack_forget()

    t2 = time.time()

    # Handle overflow label
    if '_available_overflow_label' not in overflow_label_holder:
        overflow_label_holder['_available_overflow_label'] = ctk.CTkLabel(
            available_list,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=("#6b7280", "#9ca3af")
        )

    overflow_lbl = overflow_label_holder['_available_overflow_label']
    if len(available) > MAX_DISPLAY:
        overflow_lbl.configure(text=f"... et {len(available) - MAX_DISPLAY} autres")
        overflow_lbl.pack(pady=10)
    else:
        overflow_lbl.pack_forget()

    print(f"_update_available_list: pool={t1-t0:.3f}s, update={t2-t1:.3f}s, TOTAL={t2-t0:.3f}s (showing {num_to_show}/{len(available)})")


def update_selected_display(selected_ids_list: List[int], songs_by_id: Dict, **ctx):
    """Update the selected songs list display using widget recycling.

    Keyword args:
        selected_widgets, selected_list, count_label, on_selection_change.

    Returns the time taken for the selected portion (for logging by caller).
    """
    selected_widgets = ctx['selected_widgets']
    selected_list = ctx['selected_list']
    count_label = ctx['count_label']
    on_selection_change = ctx.get('on_selection_change')
    import time
    t0 = time.time()

    num_selected = len(selected_ids_list)

    # Ensure we have enough widgets in the pool
    while len(selected_widgets) < num_selected:
        widget = create_recyclable_item(selected_list, is_available=False)
        selected_widgets.append(widget)

    t1 = time.time()

    # Update visible widgets with new data
    for i, song_id in enumerate(selected_ids_list):
        song = songs_by_id.get(song_id)
        if song:
            widget = selected_widgets[i]
            update_widget_content(widget, song, is_available=False, position=i + 1)
            widget.pack(fill="x", pady=2, padx=2)

    # Hide unused widgets
    for i in range(num_selected, len(selected_widgets)):
        selected_widgets[i].pack_forget()

    t2 = time.time()

    # Update count
    count_label.configure(text=f"({num_selected})")

    # Notify parent of selection change
    if on_selection_change:
        on_selection_change()

    return t0, t1, t2
