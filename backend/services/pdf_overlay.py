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


class OverlayMixin:
    """Mixin fournissant la fusion PDF et l'ajout d'overlays.

    Requiert que la classe hote ait :
    - self._count_pdf_pages(pdf_path) -> int
    """

    # -----------------------------------------------------------------
    # MERGE
    # -----------------------------------------------------------------

    def _merge_all(self, system_pages, songs, output_path, config):
        """Fusionne tous les PDF en un seul avec pieds de page."""
        merger = PdfMerger()

        for pdf_path in system_pages:
            if os.path.exists(pdf_path):
                merger.append(pdf_path)

        system_page_count = self._count_system_pages(system_pages)

        for song in songs:
            if song.pdf_path and os.path.exists(song.pdf_path):
                try:
                    merger.append(song.pdf_path)
                except Exception as e:
                    print(f"   Erreur fusion {song.title}: {e}")

        temp_merged = output_path + ".temp"
        merger.write(temp_merged)
        merger.close()

        self._add_footers(temp_merged, output_path, config, songs, system_page_count)
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

    def _draw_page_number(self, can, config, page_num: int,
                          page_width: float):
        """Dessine le numero de page sur le canvas overlay."""
        can.setFont("Helvetica", 10)
        can.setFillColor(HexColor("#64748b"))

        positions = {
            'left': config.margin_left * mm + 10,
            'center': page_width / 2,
            'right': page_width - config.margin_right * mm - 10
        }
        x_pos = positions.get(config.page_number_position, page_width / 2)
        y_pos = 15

        text = str(page_num)
        if config.page_number_position == 'center':
            can.drawCentredString(x_pos, y_pos, text)
        elif config.page_number_position == 'right':
            can.drawRightString(x_pos, y_pos, text)
        else:
            can.drawString(x_pos, y_pos, text)

    def _draw_song_header(self, can, song_info: tuple,
                          page_width: float, page_height: float):
        """Dessine le titre/artiste en en-tete pour une page de morceau."""
        title, artist, page_in_song, total_pages = song_info
        can.setFont("Helvetica-Bold", 10)
        can.setFillColor(HexColor("#475569"))

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
                     songs, system_page_count: int):
        """Ajoute les pieds de page: numero + titre/artiste pour les morceaux."""
        reader = PdfReader(input_path)
        writer = PdfWriter()
        song_page_map = self._build_song_page_map(songs, system_page_count)

        for i, page in enumerate(reader.pages):
            page_num = i + 1
            page_box = page.mediabox
            page_width = float(page_box.width)
            page_height = float(page_box.height)

            packet = BytesIO()
            can = pdf_canvas.Canvas(packet, pagesize=(page_width, page_height))

            if config.page_numbers:
                self._draw_page_number(can, config, page_num, page_width)

            if page_num in song_page_map:
                self._draw_song_header(
                    can, song_page_map[page_num], page_width, page_height
                )

            can.save()
            packet.seek(0)
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

        with open(output_path, 'wb') as f:
            writer.write(f)
