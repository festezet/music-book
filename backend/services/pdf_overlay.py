"""
PDF merge et overlay pour Music Book.

Contient les methodes de :
- Fusion de PDF (merge)
- Ajout de pieds de page (numeros de page)
- Ajout d'en-tetes (titre/artiste sur pages de morceaux)
"""

import os
from io import BytesIO
from typing import List, Dict

from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdf_canvas
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from PyPDF2.generic import (
    ArrayObject, DictionaryObject, FloatObject,
    NameObject, NumberObject
)


class OverlayMixin:
    """Mixin fournissant la fusion PDF et l'ajout d'overlays.

    Requiert que la classe hote ait :
    - self._count_pdf_pages(pdf_path) -> int
    """

    # -----------------------------------------------------------------
    # MERGE
    # -----------------------------------------------------------------

    def _merge_all(self, system_pages, songs, output_path, config):
        """Fusionne tous les PDF en un seul avec pieds de page et liens."""
        merger = PdfMerger()
        file_offsets = {}
        system_page_count = 0

        for pdf_path in system_pages:
            if os.path.exists(pdf_path):
                basename = os.path.basename(pdf_path)
                file_offsets[basename] = system_page_count
                try:
                    reader = PdfReader(pdf_path)
                    system_page_count += len(reader.pages)
                except Exception:
                    system_page_count += 1
                merger.append(pdf_path)

        for song in songs:
            if song.pdf_path and os.path.exists(song.pdf_path):
                try:
                    merger.append(song.pdf_path)
                except Exception as e:
                    print(f"   Erreur fusion {song.title}: {e}")

        temp_merged = output_path + ".temp"
        merger.write(temp_merged)
        merger.close()

        self._add_footers(
            temp_merged, output_path, config, songs,
            system_page_count, file_offsets
        )
        os.remove(temp_merged)

    def _count_system_pages(self, system_pages) -> int:
        """Compte le nombre total de pages systeme."""
        count = 0
        for pdf_path in system_pages:
            if os.path.exists(pdf_path):
                try:
                    reader = PdfReader(pdf_path)
                    count += len(reader.pages)
                except:
                    count += 1
        return count

    # -----------------------------------------------------------------
    # SONG PAGE MAP
    # -----------------------------------------------------------------

    def _build_song_page_map(self, songs, system_page_count: int) -> dict:
        """Construit la map page_num -> (title, artist, page_in_song, total_pages)."""
        song_page_map = {}
        current_page = system_page_count + 1
        for song in songs:
            if song.pdf_path and os.path.exists(song.pdf_path):
                song_pages = self._count_pdf_pages(song.pdf_path)
            else:
                song_pages = song.pages or 1
            for p in range(song_pages):
                song_page_map[current_page + p] = (
                    song.title, song.artist, p + 1, song_pages
                )
            current_page += song_pages
        return song_page_map

    # -----------------------------------------------------------------
    # PAGE OVERLAYS
    # -----------------------------------------------------------------

    def _draw_footer(self, can, config, page_num: int,
                     total_pages: int, page_width: float):
        """Dessine le pied de page : 'Music Book' a gauche, numero x/total a droite."""
        y_pos = 15
        left_x = config.margin_left * mm + 10
        right_x = page_width - config.margin_right * mm - 10

        can.setFont("Helvetica", 9)
        can.setFillColor(HexColor("#60a5fa"))

        # Texte footer a gauche
        can.drawString(left_x, y_pos, config.footer_text)

        # Numero de page x/total selon position configuree
        page_text = f"{page_num}/{total_pages}"
        positions = {
            'left': left_x,
            'center': page_width / 2,
            'right': right_x
        }
        x_pos = positions.get(config.page_number_position, page_width / 2)
        if config.page_number_position == 'center':
            can.drawCentredString(x_pos, y_pos, page_text)
        elif config.page_number_position == 'left':
            # Eviter chevauchement avec "Music Book"
            can.drawCentredString(page_width / 2, y_pos, page_text)
        else:
            can.drawRightString(x_pos, y_pos, page_text)

    def _draw_song_header(self, can, song_info: tuple,
                          page_width: float, page_height: float):
        """Dessine le titre/artiste en en-tete pour une page de morceau."""
        title, artist, page_in_song, total_pages = song_info
        can.setFont("Helvetica-Bold", 10)
        can.setFillColor(HexColor("#60a5fa"))

        header_y = page_height - 20
        header_text = title
        if artist:
            header_text += f" - {artist}"
        if total_pages > 1:
            header_text += f" ({page_in_song}/{total_pages})"
        can.drawCentredString(page_width / 2, header_y, header_text)

    # -----------------------------------------------------------------
    # ADD FOOTERS
    # -----------------------------------------------------------------

    def _add_footers(self, input_path: str, output_path: str, config,
                     songs, system_page_count: int,
                     file_offsets: dict = None):
        """Ajoute pieds de page, liens cliquables et bookmarks PDF."""
        reader = PdfReader(input_path)
        writer = PdfWriter()
        total_pages = len(reader.pages)
        song_page_map = self._build_song_page_map(songs, system_page_count)

        for i, page in enumerate(reader.pages):
            page_num = i + 1
            page_box = page.mediabox
            page_width = float(page_box.width)
            page_height = float(page_box.height)

            packet = BytesIO()
            can = pdf_canvas.Canvas(packet, pagesize=(page_width, page_height))

            if config.page_numbers:
                self._draw_footer(can, config, page_num, total_pages, page_width)

            if page_num in song_page_map:
                self._draw_song_header(
                    can, song_page_map[page_num], page_width, page_height
                )

            can.save()
            packet.seek(0)
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

        # Liens cliquables sur TOC et index
        self._add_internal_links(writer, file_offsets or {})

        # Bookmarks PDF (outline sidebar)
        self._add_bookmarks(writer, songs)

        with open(output_path, 'wb') as f:
            writer.write(f)

    # -----------------------------------------------------------------
    # INTERNAL LINKS & BOOKMARKS
    # -----------------------------------------------------------------

    def _add_internal_links(self, writer, file_offsets):
        """Ajoute les annotations /Link sur les pages TOC et index."""
        if not hasattr(self, '_pdf_link_data') or not self._pdf_link_data:
            return

        total_pages = len(writer.pages)
        link_count = 0
        for filename, links in self._pdf_link_data.items():
            offset = file_offsets.get(filename, 0)
            for link in links:
                src_idx = offset + link['page']
                dest_idx = link['target_page']

                if not (0 <= src_idx < total_pages and
                        0 <= dest_idx < total_pages):
                    continue

                rect = link['rect']
                dest_ref = writer.pages[dest_idx].indirect_reference

                annot = DictionaryObject()
                annot.update({
                    NameObject('/Type'): NameObject('/Annot'),
                    NameObject('/Subtype'): NameObject('/Link'),
                    NameObject('/Rect'): ArrayObject([
                        FloatObject(rect[0]), FloatObject(rect[1]),
                        FloatObject(rect[2]), FloatObject(rect[3])
                    ]),
                    NameObject('/Border'): ArrayObject([
                        NumberObject(0), NumberObject(0), NumberObject(0)
                    ]),
                    NameObject('/Dest'): ArrayObject([
                        dest_ref, NameObject('/Fit')
                    ])
                })

                src_page = writer.pages[src_idx]
                if '/Annots' not in src_page:
                    src_page[NameObject('/Annots')] = ArrayObject()
                src_page['/Annots'].append(annot)
                link_count += 1

        print(f"   {link_count} liens cliquables ajoutes"
              f" ({len(self._pdf_link_data)} sections)")

    def _add_bookmarks(self, writer, songs):
        """Ajoute les bookmarks PDF (outline) pour chaque morceau."""
        for song in songs:
            page_idx = song.start_page - 1
            if 0 <= page_idx < len(writer.pages):
                title = song.title
                if song.artist:
                    title += f" \u2014 {song.artist}"
                writer.add_outline_item(title=title, page_number=page_idx)
