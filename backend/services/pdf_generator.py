#!/usr/bin/env python3
"""
Service de génération de Music Books PDF

Génère un PDF complet avec :
- Page de garde
- Table des matières
- Morceaux (fusion des PDF sources)
- Index alphabétique

Usage CLI:
    python3 pdf_generator.py --book-id 1
    python3 pdf_generator.py --songs 1,2,3 --title "Mon Book" --instrument guitar

Usage Python:
    from services.pdf_generator import MusicBookGenerator
    generator = MusicBookGenerator()
    output_path = generator.generate_from_book_id(1)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass

# PDF Libraries
from reportlab.lib.pagesizes import A4, LETTER, A5, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image
)
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# Ajouter le chemin backend pour imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class SongInfo:
    """Informations d'un morceau pour la génération"""
    id: int
    title: str
    artist: str
    pdf_path: str
    pages: int
    instruments: List[str]
    source: str = None
    type: str = None
    genre: str = None  # Genre musical (rock, pop, chanson francaise, etc.)
    start_page: int = 0  # Calculé lors de la génération


@dataclass
class BookConfig:
    """Configuration du book à générer"""
    title: str
    instrument: str = "guitar"
    include_cover: bool = True
    include_toc: bool = True
    # Index options
    include_index_title: bool = True      # Index par titre (A-Z)
    include_index_artist: bool = False    # Index par artiste (A-Z)
    include_index_genre: bool = False     # Index par genre
    # Page numbering
    page_numbers: bool = True
    page_number_position: str = "center"  # left, center, right
    # Page format
    page_format: str = "A4"               # A4, LETTER, A5
    orientation: str = "portrait"         # portrait, landscape
    # Margins (in mm)
    margin_top: int = 20
    margin_bottom: int = 20
    margin_left: int = 15
    margin_right: int = 15
    # Output
    output_dir: str = None
    filename_pattern: str = "{title}_{instrument}_{date}"


# =============================================================================
# MUSIC BOOK GENERATOR
# =============================================================================

class MusicBookGenerator:
    """Générateur de Music Books PDF"""

    # Couleurs du thème
    PRIMARY_COLOR = HexColor("#2563eb")
    SECONDARY_COLOR = HexColor("#64748b")
    TEXT_COLOR = HexColor("#1e293b")

    def __init__(self, output_dir: str = None):
        """
        Initialise le générateur

        Args:
            output_dir: Répertoire de sortie (défaut: data/generated/)
        """
        self.output_dir = output_dir or self._get_default_output_dir()
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)

        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_styles()

    def _get_default_output_dir(self) -> str:
        """Retourne le répertoire de sortie par défaut"""
        return "/data/projects/music-book/data/generated"

    def _get_page_size(self, config: BookConfig):
        """Retourne la taille de page selon la configuration"""
        sizes = {
            'A4': A4,
            'LETTER': LETTER,
            'A5': A5
        }
        page_size = sizes.get(config.page_format.upper(), A4)
        if config.orientation == 'landscape':
            page_size = landscape(page_size)
        return page_size

    def _setup_styles(self):
        """Configure les styles personnalisés"""
        # Titre principal (page de garde)
        self.styles.add(ParagraphStyle(
            name='BookTitle',
            parent=self.styles['Title'],
            fontSize=36,
            textColor=self.PRIMARY_COLOR,
            alignment=TA_CENTER,
            spaceAfter=30
        ))

        # Sous-titre
        self.styles.add(ParagraphStyle(
            name='BookSubtitle',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=self.SECONDARY_COLOR,
            alignment=TA_CENTER,
            spaceAfter=20
        ))

        # Titre TOC
        self.styles.add(ParagraphStyle(
            name='TOCTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            alignment=TA_CENTER,
            spaceBefore=20,
            spaceAfter=30
        ))

        # Entrée TOC
        self.styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=self.styles['Normal'],
            fontSize=12,
            leftIndent=20,
            spaceBefore=8,
            spaceAfter=8
        ))

        # Titre Index
        self.styles.add(ParagraphStyle(
            name='IndexTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            alignment=TA_CENTER,
            spaceBefore=20,
            spaceAfter=30
        ))

    # =========================================================================
    # GÉNÉRATION PRINCIPALE
    # =========================================================================

    def generate(self, songs: List[SongInfo], config: BookConfig) -> str:
        """
        Génère un Music Book PDF

        Args:
            songs: Liste des morceaux à inclure
            config: Configuration du book

        Returns:
            Chemin du PDF généré
        """
        print(f"\n{'='*60}")
        print(f"Generation: {config.title}")
        print(f"{'='*60}")
        print(f"{len(songs)} morceaux")
        print(f"Instrument: {config.instrument}")

        # Fichiers temporaires
        temp_files = []

        try:
            # PHASE 1: Générer les pages système et compter leurs pages réelles
            system_page_count = 0

            # 1. Page de garde
            if config.include_cover:
                cover_path = self._generate_cover(config, songs)
                temp_files.append(cover_path)
                cover_pages = self._count_pdf_pages(cover_path)
                system_page_count += cover_pages
                print(f"Page de garde generee ({cover_pages} page(s))")

            # 2. Table des matières (avec numéros temporaires, sera recalculée)
            if config.include_toc:
                # Première passe: estimer les start_page pour la TOC
                self._estimate_start_pages(songs, config)
                toc_path = self._generate_toc(songs, config)
                temp_files.append(toc_path)
                toc_pages = self._count_pdf_pages(toc_path)
                system_page_count += toc_pages
                print(f"Table des matieres generee ({toc_pages} page(s))")

            # 3. Index alphabétiques
            if config.include_index_title:
                # Estimer les start_page pour l'index
                self._estimate_start_pages(songs, config)
                index_path = self._generate_index_by_title(songs, config)
                temp_files.append(index_path)
                index_pages = self._count_pdf_pages(index_path)
                system_page_count += index_pages
                print(f"Index par titre genere ({index_pages} page(s))")

            if config.include_index_artist:
                self._estimate_start_pages(songs, config)
                index_path = self._generate_index_by_artist(songs, config)
                temp_files.append(index_path)
                index_pages = self._count_pdf_pages(index_path)
                system_page_count += index_pages
                print(f"Index par artiste genere ({index_pages} page(s))")

            if config.include_index_genre:
                self._estimate_start_pages(songs, config)
                index_path = self._generate_index_by_genre(songs, config)
                temp_files.append(index_path)
                index_pages = self._count_pdf_pages(index_path)
                system_page_count += index_pages
                print(f"Index par genre genere ({index_pages} page(s))")

            # PHASE 2: Calculer les vraies pages de départ maintenant qu'on connait
            # le nombre exact de pages système
            # IMPORTANT: Compter les pages réelles des PDF sources (pas la valeur BDD)
            print(f"\nPages systeme: {system_page_count}")
            current_page = system_page_count + 1
            for song in songs:
                song.start_page = current_page
                # Compter les pages réelles du PDF source
                if song.pdf_path and os.path.exists(song.pdf_path):
                    actual_pages = self._count_pdf_pages(song.pdf_path)
                    song.pages = actual_pages  # Mettre à jour avec la valeur réelle
                else:
                    actual_pages = song.pages or 1
                current_page += actual_pages
                print(f"  {song.title}: page {song.start_page} ({actual_pages} page(s))")

            # PHASE 3: Regénérer TOC et Index avec les bons numéros de page
            # On doit supprimer les anciens fichiers et les regénérer
            temp_files_updated = []

            if config.include_cover:
                temp_files_updated.append(temp_files[0])  # Cover reste

            idx = 1 if config.include_cover else 0

            if config.include_toc:
                # Supprimer l'ancien et régénérer
                old_toc = temp_files[idx]
                if os.path.exists(old_toc):
                    os.remove(old_toc)
                toc_path = self._generate_toc(songs, config)
                temp_files_updated.append(toc_path)
                idx += 1
                print(f"Table des matieres regeneree avec pagination correcte")

            if config.include_index_title:
                old_index = temp_files[idx]
                if os.path.exists(old_index):
                    os.remove(old_index)
                index_path = self._generate_index_by_title(songs, config)
                temp_files_updated.append(index_path)
                idx += 1
                print(f"Index par titre regenere avec pagination correcte")

            if config.include_index_artist:
                old_index = temp_files[idx]
                if os.path.exists(old_index):
                    os.remove(old_index)
                index_path = self._generate_index_by_artist(songs, config)
                temp_files_updated.append(index_path)
                idx += 1
                print(f"Index par artiste regenere avec pagination correcte")

            if config.include_index_genre:
                old_index = temp_files[idx]
                if os.path.exists(old_index):
                    os.remove(old_index)
                index_path = self._generate_index_by_genre(songs, config)
                temp_files_updated.append(index_path)
                print(f"Index par genre regenere avec pagination correcte")

            temp_files = temp_files_updated

            # 4. Fusionner les PDF des morceaux
            print(f"\nFusion des {len(songs)} morceaux...")
            songs_with_pdf = [s for s in songs if s.pdf_path and Path(s.pdf_path).exists()]
            missing = len(songs) - len(songs_with_pdf)
            if missing > 0:
                print(f"   {missing} morceaux sans PDF (ignores)")

            # 5. Fusion finale
            output_filename = self._get_output_filename(config, len(songs))
            output_path = os.path.join(self.output_dir, output_filename)

            # Ordre: Cover, TOC, Index, puis Morceaux (avec pied de page titre/artiste)
            self._merge_all(temp_files, songs_with_pdf, output_path, config)
            print(f"\nPDF genere: {output_path}")

            return output_path

        finally:
            # Nettoyer les fichiers temporaires
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass

    def _count_pdf_pages(self, pdf_path: str) -> int:
        """Compte le nombre de pages d'un PDF"""
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception as e:
            print(f"Erreur comptage pages {pdf_path}: {e}")
            return 1

    def _estimate_start_pages(self, songs: List[SongInfo], config: BookConfig):
        """Estime les pages de départ (utilisé pour la première passe)"""
        current_page = 1
        if config.include_cover:
            current_page += 1
        if config.include_toc:
            toc_pages = max(1, (len(songs) // 20) + 1)
            current_page += toc_pages
        if config.include_index_title:
            current_page += max(1, (len(songs) // 25) + 1)
        if config.include_index_artist:
            current_page += max(1, (len(songs) // 20) + 1)
        if config.include_index_genre:
            current_page += max(1, (len(songs) // 25) + 1)

        for song in songs:
            song.start_page = current_page
            current_page += song.pages or 1

    def _get_output_filename(self, config: BookConfig, song_count: int = 0) -> str:
        """Génère le nom du fichier de sortie selon le pattern"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        safe_title = config.title.replace(" ", "_").replace("/", "-")

        filename = config.filename_pattern
        filename = filename.replace("{title}", safe_title)
        filename = filename.replace("{instrument}", config.instrument)
        filename = filename.replace("{date}", date_str)
        filename = filename.replace("{count}", str(song_count))

        return f"{filename}.pdf"

    # =========================================================================
    # PAGE DE GARDE
    # =========================================================================

    def _generate_cover(self, config: BookConfig, songs: List[SongInfo]) -> str:
        """Génère la page de garde"""
        temp_path = os.path.join(self.output_dir, "_temp_cover.pdf")

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=self._get_page_size(config),
            topMargin=config.margin_top * mm,
            bottomMargin=config.margin_bottom * mm,
            leftMargin=config.margin_left * mm,
            rightMargin=config.margin_right * mm
        )

        story = []

        # Espace en haut
        story.append(Spacer(1, 4*cm))

        # Icône musicale (emoji texte)
        story.append(Paragraph("🎵", self.styles['BookTitle']))
        story.append(Spacer(1, 1*cm))

        # Titre du book
        story.append(Paragraph(config.title, self.styles['BookTitle']))
        story.append(Spacer(1, 0.5*cm))

        # Instrument
        instrument_display = {
            'guitar': '🎸 Guitare',
            'bass': '🎸 Basse',
            'violin': '🎻 Violon'
        }.get(config.instrument, config.instrument)
        story.append(Paragraph(instrument_display, self.styles['BookSubtitle']))

        story.append(Spacer(1, 2*cm))

        # Statistiques
        total_pages = sum(s.pages or 1 for s in songs)
        stats_text = f"{len(songs)} morceaux • {total_pages} pages"
        story.append(Paragraph(stats_text, self.styles['BookSubtitle']))

        story.append(Spacer(1, 3*cm))

        # Date de génération
        date_str = datetime.now().strftime("%d/%m/%Y")
        story.append(Paragraph(f"Généré le {date_str}", self.styles['BookSubtitle']))

        # Générer
        doc.build(story)
        return temp_path

    # =========================================================================
    # TABLE DES MATIÈRES
    # =========================================================================

    def _generate_toc(self, songs: List[SongInfo], config: BookConfig) -> str:
        """Génère la table des matières avec numéros alignés à droite

        Note: Les liens seront ajoutés après la fusion finale via _add_toc_links()
        """
        temp_path = os.path.join(self.output_dir, "_temp_toc.pdf")

        page_size = self._get_page_size(config)
        page_width = page_size[0]
        content_width = page_width - (config.margin_left + config.margin_right) * mm

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=page_size,
            topMargin=config.margin_top * mm,
            bottomMargin=config.margin_bottom * mm,
            leftMargin=config.margin_left * mm,
            rightMargin=config.margin_right * mm
        )

        story = []

        # Titre
        story.append(Paragraph("Table des Matieres", self.styles['TOCTitle']))
        story.append(Spacer(1, 0.5*cm))

        # Style pour les entrées (bleu pour indiquer cliquable)
        toc_link_style = ParagraphStyle(
            'TOCLink',
            parent=self.styles['TOCEntry'],
            textColor=HexColor("#2563eb"),
        )

        # Créer tableau pour alignement
        toc_data = []
        for i, song in enumerate(songs, 1):
            artist_part = f" - {song.artist}" if song.artist else ""
            # Texte en bleu pour indiquer qu'il sera cliquable
            entry_text = f'<font color="#2563eb"><b>{i}.</b> {song.title}{artist_part}</font>'
            page_num = str(song.start_page)

            toc_data.append([
                Paragraph(entry_text, self.styles['TOCEntry']),
                Paragraph(f'<font color="#2563eb"><b>{page_num}</b></font>', ParagraphStyle(
                    'PageNum', parent=self.styles['TOCEntry'], alignment=TA_RIGHT
                ))
            ])

        if toc_data:
            # Largeurs: titre prend tout l'espace, numéro de page 40pt
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

    # =========================================================================
    # INDEX ALPHABÉTIQUES
    # =========================================================================

    def _generate_index_by_title(self, songs: List[SongInfo], config: BookConfig) -> str:
        """Génère l'index alphabétique par titre avec numéros alignés à droite"""
        temp_path = os.path.join(self.output_dir, "_temp_index_title.pdf")

        page_size = self._get_page_size(config)
        page_width = page_size[0]
        content_width = page_width - (config.margin_left + config.margin_right) * mm

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=page_size,
            topMargin=config.margin_top * mm,
            bottomMargin=config.margin_bottom * mm,
            leftMargin=config.margin_left * mm,
            rightMargin=config.margin_right * mm
        )

        story = []

        # Titre
        story.append(Paragraph("Index par Titre", self.styles['IndexTitle']))
        story.append(Spacer(1, 0.5*cm))

        # Trier par titre
        sorted_songs = sorted(songs, key=lambda s: s.title.lower())

        current_letter = ""
        index_data = []

        for song in sorted_songs:
            first_letter = song.title[0].upper()

            # Nouvelle lettre - flush previous data and add header
            if first_letter != current_letter:
                if index_data:
                    table = Table(index_data, colWidths=[content_width - 50, 50])
                    table.setStyle(TableStyle([
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 0),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                    ]))
                    story.append(table)
                    index_data = []

                current_letter = first_letter
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(
                    f"<b><font color='#2563eb'>{current_letter}</font></b>",
                    self.styles['Heading2']
                ))

            # Entrée avec numéro aligné à droite
            artist_part = f" ({song.artist})" if song.artist else ""
            entry_text = f"{song.title}{artist_part}"
            index_data.append([
                Paragraph(entry_text, self.styles['TOCEntry']),
                Paragraph(f"<b>{song.start_page}</b>", ParagraphStyle(
                    'PageNum', parent=self.styles['TOCEntry'], alignment=TA_RIGHT
                ))
            ])

        # Flush remaining data
        if index_data:
            table = Table(index_data, colWidths=[content_width - 50, 50])
            table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 0),
                ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
            ]))
            story.append(table)

        doc.build(story)
        return temp_path

    def _generate_index_by_artist(self, songs: List[SongInfo], config: BookConfig) -> str:
        """Génère l'index alphabétique par artiste avec numéros alignés à droite"""
        temp_path = os.path.join(self.output_dir, "_temp_index_artist.pdf")

        page_size = self._get_page_size(config)
        page_width = page_size[0]
        content_width = page_width - (config.margin_left + config.margin_right) * mm

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=page_size,
            topMargin=config.margin_top * mm,
            bottomMargin=config.margin_bottom * mm,
            leftMargin=config.margin_left * mm,
            rightMargin=config.margin_right * mm
        )

        story = []

        # Titre
        story.append(Paragraph("Index par Artiste", self.styles['IndexTitle']))
        story.append(Spacer(1, 0.5*cm))

        # Grouper par artiste
        from collections import defaultdict
        by_artist = defaultdict(list)
        for song in songs:
            artist = song.artist or "Inconnu"
            by_artist[artist].append(song)

        # Trier artistes alphabétiquement
        sorted_artists = sorted(by_artist.keys(), key=str.lower)

        current_letter = ""
        for artist in sorted_artists:
            first_letter = artist[0].upper()

            # Nouvelle lettre
            if first_letter != current_letter:
                current_letter = first_letter
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(
                    f"<b><font color='#2563eb'>{current_letter}</font></b>",
                    self.styles['Heading2']
                ))

            # Nom de l'artiste
            story.append(Paragraph(
                f"<b>{artist}</b>",
                self.styles['TOCEntry']
            ))

            # Morceaux de cet artiste avec numéros alignés à droite
            artist_songs_data = []
            for song in sorted(by_artist[artist], key=lambda s: s.title.lower()):
                artist_songs_data.append([
                    Paragraph(f"    {song.title}", self.styles['TOCEntry']),
                    Paragraph(f"<b>{song.start_page}</b>", ParagraphStyle(
                        'PageNum', parent=self.styles['TOCEntry'], alignment=TA_RIGHT
                    ))
                ])

            if artist_songs_data:
                table = Table(artist_songs_data, colWidths=[content_width - 50, 50])
                table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(table)

        doc.build(story)
        return temp_path

    def _generate_index_by_genre(self, songs: List[SongInfo], config: BookConfig) -> str:
        """Génère l'index par genre avec numéros alignés à droite"""
        temp_path = os.path.join(self.output_dir, "_temp_index_genre.pdf")

        page_size = self._get_page_size(config)
        page_width = page_size[0]
        content_width = page_width - (config.margin_left + config.margin_right) * mm

        doc = SimpleDocTemplate(
            temp_path,
            pagesize=page_size,
            topMargin=config.margin_top * mm,
            bottomMargin=config.margin_bottom * mm,
            leftMargin=config.margin_left * mm,
            rightMargin=config.margin_right * mm
        )

        story = []

        # Titre
        story.append(Paragraph("Index par Genre", self.styles['IndexTitle']))
        story.append(Spacer(1, 0.5*cm))

        # Grouper par genre musical
        from collections import defaultdict
        by_genre = defaultdict(list)
        for song in songs:
            # Utiliser le vrai genre musical, pas la source
            genre = getattr(song, 'genre', None) or "Non classe"
            by_genre[genre].append(song)

        # Trier genres alphabétiquement
        sorted_genres = sorted(by_genre.keys(), key=str.lower)

        for genre in sorted_genres:
            # Nom du genre
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(
                f"<b><font color='#2563eb'>{genre.replace('_', ' ').title()}</font></b>",
                self.styles['Heading2']
            ))

            # Morceaux de ce genre avec numéros alignés à droite
            genre_songs_data = []
            for song in sorted(by_genre[genre], key=lambda s: s.title.lower()):
                artist_part = f" ({song.artist})" if song.artist else ""
                genre_songs_data.append([
                    Paragraph(f"    {song.title}{artist_part}", self.styles['TOCEntry']),
                    Paragraph(f"<b>{song.start_page}</b>", ParagraphStyle(
                        'PageNum', parent=self.styles['TOCEntry'], alignment=TA_RIGHT
                    ))
                ])

            if genre_songs_data:
                table = Table(genre_songs_data, colWidths=[content_width - 50, 50])
                table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                    ('TOPPADDING', (0, 0), (-1, -1), 2),
                ]))
                story.append(table)

        doc.build(story)
        return temp_path

    # =========================================================================
    # FUSION PDF
    # =========================================================================

    def _merge_all(
        self,
        system_pages: List[str],
        songs: List[SongInfo],
        output_path: str,
        config: BookConfig
    ):
        """Fusionne tous les PDF en un seul avec pied de page titre/artiste pour les morceaux"""
        merger = PdfMerger()

        # 1. Pages système (cover, toc, index)
        for pdf_path in system_pages:
            if os.path.exists(pdf_path):
                merger.append(pdf_path)

        # Compter les pages système pour savoir où commencent les morceaux
        system_page_count = 0
        for pdf_path in system_pages:
            if os.path.exists(pdf_path):
                try:
                    reader = PdfReader(pdf_path)
                    system_page_count += len(reader.pages)
                except:
                    system_page_count += 1

        # 2. PDF des morceaux
        for song in songs:
            if song.pdf_path and os.path.exists(song.pdf_path):
                try:
                    merger.append(song.pdf_path)
                except Exception as e:
                    print(f"   Erreur fusion {song.title}: {e}")

        # Écrire le fichier temporaire
        temp_merged = output_path + ".temp"
        merger.write(temp_merged)
        merger.close()

        # 3. Ajouter numéros de page ET titre/artiste pour les morceaux
        self._add_footers(temp_merged, output_path, config, songs, system_page_count)
        os.remove(temp_merged)

    def _add_footers(
        self,
        input_path: str,
        output_path: str,
        config: BookConfig,
        songs: List[SongInfo],
        system_page_count: int
    ):
        """Ajoute les pieds de page: numéro + titre/artiste pour les morceaux"""
        from reportlab.pdfgen import canvas as pdf_canvas
        from io import BytesIO

        reader = PdfReader(input_path)
        writer = PdfWriter()

        # Construire la map page -> (titre, artiste, page_in_song, total_pages)
        # pour savoir quel morceau est sur quelle page
        # IMPORTANT: Utiliser le nombre réel de pages du PDF source
        song_page_map = {}  # page_num -> (title, artist, page_in_song, total_pages)
        current_page = system_page_count + 1
        for song in songs:
            # Compter les pages réelles du PDF
            if song.pdf_path and os.path.exists(song.pdf_path):
                song_pages = self._count_pdf_pages(song.pdf_path)
            else:
                song_pages = song.pages or 1
            for p in range(song_pages):
                song_page_map[current_page + p] = (song.title, song.artist, p + 1, song_pages)
            current_page += song_pages

        for i, page in enumerate(reader.pages):
            page_num = i + 1

            # Obtenir la taille réelle de la page du PDF source
            page_box = page.mediabox
            page_width = float(page_box.width)
            page_height = float(page_box.height)

            # Créer overlay
            packet = BytesIO()
            can = pdf_canvas.Canvas(packet, pagesize=(page_width, page_height))

            y_pos = 15  # Position en bas de page

            # Numéro de page (si activé)
            if config.page_numbers:
                can.setFont("Helvetica", 10)
                can.setFillColor(HexColor("#64748b"))

                positions = {
                    'left': config.margin_left * mm + 10,
                    'center': page_width / 2,
                    'right': page_width - config.margin_right * mm - 10
                }
                x_pos = positions.get(config.page_number_position, page_width / 2)

                text = str(page_num)
                if config.page_number_position == 'center':
                    can.drawCentredString(x_pos, y_pos, text)
                elif config.page_number_position == 'right':
                    can.drawRightString(x_pos, y_pos, text)
                else:
                    can.drawString(x_pos, y_pos, text)

            # Titre/Artiste en EN-TETE pour les pages de morceaux
            if page_num in song_page_map:
                title, artist, page_in_song, total_pages = song_page_map[page_num]
                can.setFont("Helvetica-Bold", 10)
                can.setFillColor(HexColor("#475569"))

                # Titre centré en haut de page
                header_y = page_height - 20  # 20 points du haut
                header_text = title
                if artist:
                    header_text += f" - {artist}"
                if total_pages > 1:
                    header_text += f" ({page_in_song}/{total_pages})"
                can.drawCentredString(page_width / 2, header_y, header_text)

            can.save()

            # Fusionner overlay avec page
            packet.seek(0)
            overlay = PdfReader(packet)
            page.merge_page(overlay.pages[0])
            writer.add_page(page)

        # Écrire le fichier final
        with open(output_path, 'wb') as f:
            writer.write(f)

    # =========================================================================
    # MÉTHODES UTILITAIRES
    # =========================================================================

    def generate_from_book_id(self, book_id: int) -> str:
        """
        Génère un PDF à partir d'un book en base de données

        Args:
            book_id: ID du book dans la BDD

        Returns:
            Chemin du PDF généré
        """
        from app import app, db
        from models.book import Book
        from models.song import Song

        with app.app_context():
            book = Book.query.get(book_id)
            if not book:
                raise ValueError(f"Book ID {book_id} non trouvé")

            # Récupérer les morceaux ordonnés
            songs_data = []
            for bs in sorted(book.book_songs, key=lambda x: x.position):
                song = bs.song
                songs_data.append(SongInfo(
                    id=song.id,
                    title=song.title,
                    artist=song.artist or "",
                    pdf_path=song.pdf_path,
                    pages=song.pages or 1,
                    instruments=json.loads(song.instruments) if song.instruments else [],
                    source=song.source,
                    type=song.type,
                    genre=song.genre
                ))

            config = BookConfig(
                title=book.title,
                instrument=book.instrument,
                include_cover=getattr(book, 'include_cover', True),
                include_toc=getattr(book, 'include_toc', True),
                include_index_title=getattr(book, 'include_index', True),
                include_index_artist=False,
                include_index_genre=False,
            )

            return self.generate(songs_data, config)

    def generate_from_song_ids(
        self,
        song_ids: List[int],
        title: str = "Music Book",
        instrument: str = "guitar",
        include_cover: bool = True,
        include_toc: bool = True,
        include_index: bool = True,
        # Nouvelles options
        include_index_artist: bool = False,
        include_index_genre: bool = False,
        page_numbers: bool = True,
        page_number_position: str = "center",
        page_format: str = "A4",
        orientation: str = "portrait",
        margin_top: int = 20,
        margin_bottom: int = 20,
        margin_left: int = 15,
        margin_right: int = 15,
        filename_pattern: str = "{title}_{instrument}_{date}"
    ) -> str:
        """
        Génère un PDF à partir d'une liste d'IDs de morceaux

        Args:
            song_ids: Liste des IDs de morceaux
            title: Titre du book
            instrument: Instrument cible
            include_cover: Inclure page de garde
            include_toc: Inclure table des matières
            include_index: Inclure index par titre
            include_index_artist: Inclure index par artiste
            include_index_genre: Inclure index par genre
            page_numbers: Afficher numéros de page
            page_number_position: Position (left, center, right)
            page_format: Format (A4, LETTER, A5)
            orientation: Orientation (portrait, landscape)
            margin_*: Marges en mm
            filename_pattern: Pattern du nom de fichier

        Returns:
            Chemin du PDF généré
        """
        from app import app, db
        from models.song import Song

        with app.app_context():
            songs_data = []
            for song_id in song_ids:
                song = Song.query.get(song_id)
                if song:
                    songs_data.append(SongInfo(
                        id=song.id,
                        title=song.title,
                        artist=song.artist or "",
                        pdf_path=song.pdf_path,
                        pages=song.pages or 1,
                        instruments=json.loads(song.instruments) if song.instruments else [],
                        source=song.source,
                        type=song.type,
                        genre=song.genre
                    ))

            config = BookConfig(
                title=title,
                instrument=instrument,
                include_cover=include_cover,
                include_toc=include_toc,
                include_index_title=include_index,
                include_index_artist=include_index_artist,
                include_index_genre=include_index_genre,
                page_numbers=page_numbers,
                page_number_position=page_number_position,
                page_format=page_format,
                orientation=orientation,
                margin_top=margin_top,
                margin_bottom=margin_bottom,
                margin_left=margin_left,
                margin_right=margin_right,
                filename_pattern=filename_pattern
            )

            return self.generate(songs_data, config)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Générateur de Music Books PDF")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--book-id', type=int, help="ID du book en base de données")
    group.add_argument('--songs', type=str, help="Liste d'IDs de morceaux (ex: 1,2,3)")

    parser.add_argument('--title', type=str, default="Music Book", help="Titre du book")
    parser.add_argument('--instrument', type=str, default="guitar",
                        choices=['guitar', 'bass', 'violin'], help="Instrument")
    parser.add_argument('--no-cover', action='store_true', help="Sans page de garde")
    parser.add_argument('--no-toc', action='store_true', help="Sans table des matières")
    parser.add_argument('--no-index', action='store_true', help="Sans index")
    parser.add_argument('--output-dir', type=str, help="Répertoire de sortie")

    args = parser.parse_args()

    generator = MusicBookGenerator(output_dir=args.output_dir)

    try:
        if args.book_id:
            output_path = generator.generate_from_book_id(args.book_id)
        else:
            song_ids = [int(x.strip()) for x in args.songs.split(',')]
            output_path = generator.generate_from_song_ids(
                song_ids=song_ids,
                title=args.title,
                instrument=args.instrument,
                include_cover=not args.no_cover,
                include_toc=not args.no_toc,
                include_index=not args.no_index
            )

        print(f"\n🎉 Succès! PDF généré: {output_path}")

    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
