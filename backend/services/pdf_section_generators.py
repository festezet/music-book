"""
Generateurs de sections PDF pour Music Book.

Contient les methodes de generation de :
- Page de garde (cover)
- Table des matieres (TOC)
- Index alphabetiques (par titre, artiste, genre)
"""

import os
from collections import defaultdict
from datetime import datetime
from typing import List

from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer


class SectionGeneratorMixin:
    """Mixin fournissant la generation de cover, TOC et index.

    Requiert que la classe hote ait :
    - self.output_dir (str)
    - self.styles (reportlab styles)
    - self._get_page_size(config) -> page_size
    """

    # -----------------------------------------------------------------
    # COVER
    # -----------------------------------------------------------------

    def _generate_cover(self, config, songs) -> str:
        """Genere la page de garde."""
        temp_path = os.path.join(self.output_dir, "_temp_cover.pdf")

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=self._get_page_size(config),
            topMargin=config.margin_top * mm,
            bottomMargin=config.margin_bottom * mm,
            leftMargin=config.margin_left * mm,
            rightMargin=config.margin_right * mm
        )

        story = self._build_cover_story(config, songs)
        doc.build(story)
        return temp_path

    def _build_cover_story(self, config, songs) -> list:
        """Construit le contenu de la page de garde."""
        story = [Spacer(1, 4 * cm)]

        story.append(Paragraph("\U0001f3b5", self.styles['BookTitle']))
        story.append(Spacer(1, 1 * cm))
        story.append(Paragraph(config.title, self.styles['BookTitle']))
        story.append(Spacer(1, 0.5 * cm))

        instrument_display = {
            'guitar': '\U0001f3b8 Guitare',
            'bass': '\U0001f3b8 Basse',
            'violin': '\U0001f3bb Violon'
        }.get(config.instrument, config.instrument)
        story.append(Paragraph(instrument_display, self.styles['BookSubtitle']))
        story.append(Spacer(1, 2 * cm))

        total_pages = sum(s.pages or 1 for s in songs)
        stats_text = f"{len(songs)} morceaux \u2022 {total_pages} pages"
        story.append(Paragraph(stats_text, self.styles['BookSubtitle']))
        story.append(Spacer(1, 3 * cm))

        date_str = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(f"G\u00e9n\u00e9r\u00e9 le {date_str}", self.styles['BookSubtitle']))
        return story

    # -----------------------------------------------------------------
    # TABLE DES MATIERES
    # -----------------------------------------------------------------

    def _generate_toc(self, songs, config) -> str:
        """Genere la table des matieres avec canvas pour liens cliquables."""
        temp_path = os.path.join(self.output_dir, "_temp_toc.pdf")
        page_size = self._get_page_size(config)
        w, h = page_size

        left = config.margin_left * mm
        right = w - config.margin_right * mm
        top = h - config.margin_top * mm
        bottom = config.margin_bottom * mm
        row_height = 26

        c = pdf_canvas.Canvas(temp_path, pagesize=page_size)
        link_data = []
        toc_page = 0

        def draw_title(y_pos):
            c.setFont("Helvetica-Bold", 22)
            c.setFillColor(HexColor("#2563eb"))
            c.drawString(left, y_pos, "Table des Matieres")
            y_pos -= 12
            c.setStrokeColor(HexColor("#2563eb"))
            c.setLineWidth(0.8)
            c.line(left, y_pos, right, y_pos)
            return y_pos - 20

        y = draw_title(top - 10)

        for i, song in enumerate(songs, 1):
            if y - row_height < bottom:
                c.showPage()
                toc_page += 1
                y = top - 20

            # Entry number + title + artist
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(HexColor("#2563eb"))
            num_str = f"{i}."
            c.drawString(left + 5, y, num_str)

            c.setFont("Helvetica", 11)
            title_text = song.title
            if song.artist:
                title_text += f"  —  {song.artist}"
            title_x = left + 30
            c.drawString(title_x, y, title_text)

            # Page number right-aligned
            c.setFont("Helvetica-Bold", 11)
            page_str = str(song.start_page)
            c.drawRightString(right, y, page_str)

            # Dot leaders
            c.setFont("Helvetica", 7)
            c.setFillColor(HexColor("#64748b"))
            title_w = c.stringWidth(title_text, "Helvetica", 11)
            page_w = c.stringWidth(page_str, "Helvetica-Bold", 11)
            dots_start = title_x + title_w + 8
            dots_end = right - page_w - 8
            if dots_end > dots_start:
                dot_unit = c.stringWidth(" . ", "Helvetica", 7)
                if dot_unit > 0:
                    dots = " . " * int((dots_end - dots_start) / dot_unit)
                    c.drawString(dots_start, y, dots)

            link_data.append({
                'page': toc_page,
                'rect': (left, y - 6, right, y + 14),
                'target_page': song.start_page - 1
            })

            y -= row_height

        c.save()
        self._pdf_link_data['_temp_toc.pdf'] = link_data
        return temp_path

    # -----------------------------------------------------------------
    # INDEX CANVAS HELPERS
    # -----------------------------------------------------------------

    def _init_index_canvas(self, config, temp_filename):
        """Initialise un canvas et les parametres de layout pour un index."""
        temp_path = os.path.join(self.output_dir, temp_filename)
        page_size = self._get_page_size(config)
        w, h = page_size
        c = pdf_canvas.Canvas(temp_path, pagesize=page_size)
        layout = {
            'left': config.margin_left * mm,
            'right': w - config.margin_right * mm,
            'top': h - config.margin_top * mm,
            'bottom': config.margin_bottom * mm,
            'row_height': 22,
        }
        return c, layout, temp_path

    def _draw_index_title(self, c, layout, title):
        """Dessine le titre d'un index avec ligne de separation."""
        y = layout['top'] - 10
        c.setFont("Helvetica-Bold", 22)
        c.setFillColor(HexColor("#2563eb"))
        c.drawString(layout['left'], y, title)
        y -= 12
        c.setStrokeColor(HexColor("#2563eb"))
        c.setLineWidth(0.8)
        c.line(layout['left'], y, layout['right'], y)
        return y - 20

    def _draw_section_header(self, c, layout, y, text, current_page):
        """Dessine un en-tete de section (lettre ou nom de groupe)."""
        needed = layout['row_height'] + 28
        if y - needed < layout['bottom']:
            c.showPage()
            current_page += 1
            y = layout['top'] - 20
        y -= 8
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(HexColor("#2563eb"))
        c.drawString(layout['left'], y, text)
        y -= layout['row_height']
        return y, current_page

    def _draw_entry_line(self, c, layout, y, text, page_str, indent=15):
        """Dessine une ligne d'entree avec dot leaders. Retourne le rect."""
        left, right = layout['left'], layout['right']
        text_x = left + indent

        c.setFont("Helvetica", 11)
        c.setFillColor(HexColor("#1e293b"))
        c.drawString(text_x, y, text)

        c.setFont("Helvetica-Bold", 11)
        c.drawRightString(right, y, page_str)

        c.setFont("Helvetica", 7)
        c.setFillColor(HexColor("#64748b"))
        text_w = c.stringWidth(text, "Helvetica", 11)
        page_w = c.stringWidth(page_str, "Helvetica-Bold", 11)
        dots_start = text_x + text_w + 8
        dots_end = right - page_w - 8
        if dots_end > dots_start:
            dot_unit = c.stringWidth(" . ", "Helvetica", 7)
            if dot_unit > 0:
                dots = " . " * int((dots_end - dots_start) / dot_unit)
                c.drawString(dots_start, y, dots)

        return (left, y - 6, right, y + 14)

    def _check_page_break(self, c, layout, y, current_page):
        """Verifie si un saut de page est necessaire."""
        if y - layout['row_height'] < layout['bottom']:
            c.showPage()
            current_page += 1
            y = layout['top'] - 20
        return y, current_page

    # -----------------------------------------------------------------
    # INDEX PAR TITRE
    # -----------------------------------------------------------------

    def _generate_index_by_title(self, songs, config) -> str:
        """Genere l'index alphabetique par titre avec liens cliquables."""
        c, layout, temp_path = self._init_index_canvas(
            config, "_temp_index_title.pdf"
        )
        link_data = []
        current_page = 0

        y = self._draw_index_title(c, layout, "Index par Titre")

        sorted_songs = sorted(songs, key=lambda s: s.title.lower())
        current_letter = ""

        for song in sorted_songs:
            first_letter = song.title[0].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                y, current_page = self._draw_section_header(
                    c, layout, y, current_letter, current_page
                )

            y, current_page = self._check_page_break(
                c, layout, y, current_page
            )

            artist_part = f" ({song.artist})" if song.artist else ""
            text = f"{song.title}{artist_part}"
            rect = self._draw_entry_line(c, layout, y, text, str(song.start_page))
            link_data.append({
                'page': current_page,
                'rect': rect,
                'target_page': song.start_page - 1
            })
            y -= layout['row_height']

        c.save()
        self._pdf_link_data['_temp_index_title.pdf'] = link_data
        return temp_path

    # -----------------------------------------------------------------
    # INDEX PAR ARTISTE
    # -----------------------------------------------------------------

    def _generate_index_by_artist(self, songs, config) -> str:
        """Genere l'index alphabetique par artiste avec liens cliquables."""
        c, layout, temp_path = self._init_index_canvas(
            config, "_temp_index_artist.pdf"
        )
        link_data = []
        current_page = 0

        y = self._draw_index_title(c, layout, "Index par Artiste")

        by_artist = defaultdict(list)
        for song in songs:
            by_artist[song.artist or "Inconnu"].append(song)

        current_letter = ""
        for artist in sorted(by_artist.keys(), key=str.lower):
            first_letter = artist[0].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                y, current_page = self._draw_section_header(
                    c, layout, y, current_letter, current_page
                )

            # Nom artiste en sous-titre
            y, current_page = self._check_page_break(
                c, layout, y, current_page
            )
            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(HexColor("#1e293b"))
            c.drawString(layout['left'] + 5, y, artist)
            y -= layout['row_height']

            for song in sorted(by_artist[artist], key=lambda s: s.title.lower()):
                y, current_page = self._check_page_break(
                    c, layout, y, current_page
                )
                rect = self._draw_entry_line(
                    c, layout, y, song.title, str(song.start_page), indent=25
                )
                link_data.append({
                    'page': current_page,
                    'rect': rect,
                    'target_page': song.start_page - 1
                })
                y -= layout['row_height']

        c.save()
        self._pdf_link_data['_temp_index_artist.pdf'] = link_data
        return temp_path

    # -----------------------------------------------------------------
    # INDEX PAR GENRE
    # -----------------------------------------------------------------

    def _generate_index_by_genre(self, songs, config) -> str:
        """Genere l'index par genre avec liens cliquables."""
        c, layout, temp_path = self._init_index_canvas(
            config, "_temp_index_genre.pdf"
        )
        link_data = []
        current_page = 0

        y = self._draw_index_title(c, layout, "Index par Genre")

        by_genre = defaultdict(list)
        for song in songs:
            genre = getattr(song, 'genre', None) or "Non classe"
            by_genre[genre].append(song)

        for genre in sorted(by_genre.keys(), key=str.lower):
            genre_display = genre.replace('_', ' ').title()
            y, current_page = self._draw_section_header(
                c, layout, y, genre_display, current_page
            )

            for song in sorted(by_genre[genre], key=lambda s: s.title.lower()):
                y, current_page = self._check_page_break(
                    c, layout, y, current_page
                )
                artist_part = f" ({song.artist})" if song.artist else ""
                text = f"{song.title}{artist_part}"
                rect = self._draw_entry_line(
                    c, layout, y, text, str(song.start_page)
                )
                link_data.append({
                    'page': current_page,
                    'rect': rect,
                    'target_page': song.start_page - 1
                })
                y -= layout['row_height']

        c.save()
        self._pdf_link_data['_temp_index_genre.pdf'] = link_data
        return temp_path
