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
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)


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
        """Genere la table des matieres avec numeros alignes a droite."""
        temp_path = os.path.join(self.output_dir, "_temp_toc.pdf")

        page_size = self._get_page_size(config)
        content_width = page_size[0] - (config.margin_left + config.margin_right) * mm

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=page_size,
            topMargin=config.margin_top * mm,
            bottomMargin=config.margin_bottom * mm,
            leftMargin=config.margin_left * mm,
            rightMargin=config.margin_right * mm
        )

        story = [
            Paragraph("Table des Matieres", self.styles['TOCTitle']),
            Spacer(1, 0.5 * cm)
        ]

        toc_data = self._build_toc_entries(songs)

        if toc_data:
            table = Table(toc_data, colWidths=[content_width - 50, 50])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(table)

        doc.build(story)
        return temp_path

    def _build_toc_entries(self, songs) -> list:
        """Construit les lignes de la table des matieres."""
        toc_data = []
        for i, song in enumerate(songs, 1):
            artist_part = f" - {song.artist}" if song.artist else ""
            entry_text = (
                f'<font color="#2563eb"><b>{i}.</b> '
                f'{song.title}{artist_part}</font>'
            )
            page_num = str(song.start_page)

            toc_data.append([
                Paragraph(entry_text, self.styles['TOCEntry']),
                Paragraph(
                    f'<font color="#2563eb"><b>{page_num}</b></font>',
                    ParagraphStyle(
                        'PageNum', parent=self.styles['TOCEntry'],
                        alignment=TA_RIGHT
                    )
                )
            ])
        return toc_data

    # -----------------------------------------------------------------
    # INDEX HELPERS
    # -----------------------------------------------------------------

    def _create_index_doc(self, config, temp_filename: str):
        """Cree un SimpleDocTemplate pour un index.

        Returns:
            (doc, content_width, temp_path)
        """
        temp_path = os.path.join(self.output_dir, temp_filename)
        page_size = self._get_page_size(config)
        content_width = page_size[0] - (config.margin_left + config.margin_right) * mm

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=page_size,
            topMargin=config.margin_top * mm,
            bottomMargin=config.margin_bottom * mm,
            leftMargin=config.margin_left * mm,
            rightMargin=config.margin_right * mm
        )
        return doc, content_width, temp_path

    def _make_index_table(self, data: list, content_width: float) -> Table:
        """Cree un Table ReportLab formate pour un index."""
        table = Table(data, colWidths=[content_width - 50, 50])
        table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        return table

    def _make_index_entry(self, text: str, page: int) -> list:
        """Cree une ligne [texte, numero de page] pour un index."""
        return [
            Paragraph(text, self.styles['TOCEntry']),
            Paragraph(f"<b>{page}</b>", ParagraphStyle(
                'PageNum', parent=self.styles['TOCEntry'], alignment=TA_RIGHT
            ))
        ]

    def _add_letter_header(self, story: list, letter: str):
        """Ajoute un en-tete de lettre dans un index."""
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(
            f"<b><font color='#2563eb'>{letter}</font></b>",
            self.styles['Heading2']
        ))

    # -----------------------------------------------------------------
    # INDEX PAR TITRE
    # -----------------------------------------------------------------

    def _generate_index_by_title(self, songs, config) -> str:
        """Genere l'index alphabetique par titre."""
        doc, content_width, temp_path = self._create_index_doc(
            config, "_temp_index_title.pdf"
        )

        story = [
            Paragraph("Index par Titre", self.styles['IndexTitle']),
            Spacer(1, 0.5 * cm)
        ]

        sorted_songs = sorted(songs, key=lambda s: s.title.lower())
        current_letter = ""
        index_data = []

        for song in sorted_songs:
            first_letter = song.title[0].upper()
            if first_letter != current_letter:
                if index_data:
                    story.append(self._make_index_table(index_data, content_width))
                    index_data = []
                current_letter = first_letter
                self._add_letter_header(story, current_letter)

            artist_part = f" ({song.artist})" if song.artist else ""
            index_data.append(self._make_index_entry(
                f"{song.title}{artist_part}", song.start_page
            ))

        if index_data:
            story.append(self._make_index_table(index_data, content_width))

        doc.build(story)
        return temp_path

    # -----------------------------------------------------------------
    # INDEX PAR ARTISTE
    # -----------------------------------------------------------------

    def _generate_index_by_artist(self, songs, config) -> str:
        """Genere l'index alphabetique par artiste."""
        doc, content_width, temp_path = self._create_index_doc(
            config, "_temp_index_artist.pdf"
        )

        story = [
            Paragraph("Index par Artiste", self.styles['IndexTitle']),
            Spacer(1, 0.5 * cm)
        ]

        by_artist = defaultdict(list)
        for song in songs:
            by_artist[song.artist or "Inconnu"].append(song)

        current_letter = ""
        for artist in sorted(by_artist.keys(), key=str.lower):
            first_letter = artist[0].upper()
            if first_letter != current_letter:
                current_letter = first_letter
                self._add_letter_header(story, current_letter)

            story.append(Paragraph(f"<b>{artist}</b>", self.styles['TOCEntry']))

            entries = [
                self._make_index_entry(f"    {s.title}", s.start_page)
                for s in sorted(by_artist[artist], key=lambda s: s.title.lower())
            ]
            if entries:
                story.append(self._make_index_table(entries, content_width))

        doc.build(story)
        return temp_path

    # -----------------------------------------------------------------
    # INDEX PAR GENRE
    # -----------------------------------------------------------------

    def _generate_index_by_genre(self, songs, config) -> str:
        """Genere l'index par genre."""
        doc, content_width, temp_path = self._create_index_doc(
            config, "_temp_index_genre.pdf"
        )

        story = [
            Paragraph("Index par Genre", self.styles['IndexTitle']),
            Spacer(1, 0.5 * cm)
        ]

        by_genre = defaultdict(list)
        for song in songs:
            genre = getattr(song, 'genre', None) or "Non classe"
            by_genre[genre].append(song)

        for genre in sorted(by_genre.keys(), key=str.lower):
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph(
                f"<b><font color='#2563eb'>{genre.replace('_', ' ').title()}</font></b>",
                self.styles['Heading2']
            ))

            entries = []
            for song in sorted(by_genre[genre], key=lambda s: s.title.lower()):
                artist_part = f" ({song.artist})" if song.artist else ""
                entries.append(self._make_index_entry(
                    f"    {song.title}{artist_part}", song.start_page
                ))

            if entries:
                story.append(self._make_index_table(entries, content_width))

        doc.build(story)
        return temp_path
