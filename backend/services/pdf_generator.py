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
from typing import List
from dataclasses import dataclass

# PDF Libraries
from reportlab.lib.pagesizes import A4, LETTER, A5, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor
from PyPDF2 import PdfReader

# Ajouter le chemin backend pour imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Mixins
from services.pdf_section_generators import SectionGeneratorMixin
from services.pdf_overlay import OverlayMixin


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

class MusicBookGenerator(SectionGeneratorMixin, OverlayMixin):
    """Generateur de Music Books PDF.

    Herite de :
    - SectionGeneratorMixin : cover, TOC, index generation
    - OverlayMixin : merge, footers, page overlays
    """

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
        return str(Path(__file__).parent.parent.parent / "data" / "generated")

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
        """Configure les styles personnalises pour le book PDF."""
        style_defs = [
            ('BookTitle', 'Title', dict(fontSize=36, textColor=self.PRIMARY_COLOR,
                                        alignment=TA_CENTER, spaceAfter=30)),
            ('BookSubtitle', 'Normal', dict(fontSize=18, textColor=self.SECONDARY_COLOR,
                                            alignment=TA_CENTER, spaceAfter=20)),
            ('TOCTitle', 'Heading1', dict(fontSize=24, textColor=self.PRIMARY_COLOR,
                                          alignment=TA_CENTER, spaceBefore=20, spaceAfter=30)),
            ('TOCEntry', 'Normal', dict(fontSize=12, leftIndent=20,
                                        spaceBefore=8, spaceAfter=8)),
            ('IndexTitle', 'Heading1', dict(fontSize=24, textColor=self.PRIMARY_COLOR,
                                            alignment=TA_CENTER, spaceBefore=20, spaceAfter=30)),
        ]
        for name, parent_name, kwargs in style_defs:
            self.styles.add(ParagraphStyle(name=name, parent=self.styles[parent_name], **kwargs))

    # =========================================================================
    # GÉNÉRATION PRINCIPALE
    # =========================================================================

    def generate(self, songs: List[SongInfo], config: BookConfig) -> str:
        """
        Genere un Music Book PDF

        Args:
            songs: Liste des morceaux a inclure
            config: Configuration du book

        Returns:
            Chemin du PDF genere
        """
        print(f"\n{'='*60}")
        print(f"Generation: {config.title}")
        print(f"{'='*60}")
        print(f"{len(songs)} morceaux")
        print(f"Instrument: {config.instrument}")

        temp_files = []

        try:
            # PHASE 1: Pages systeme (estimation)
            temp_files, system_page_count = self._generate_system_pages(
                songs, config
            )

            # PHASE 2: Calculer les vraies pages de depart
            self._compute_song_start_pages(songs, system_page_count)

            # PHASE 3: Regenerer TOC/Index avec pagination correcte
            temp_files = self._regenerate_system_pages(
                temp_files, songs, config
            )

            # PHASE 4: Fusion finale
            return self._merge_and_finalize(temp_files, songs, config)

        finally:
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass

    def _generate_system_pages(
        self, songs: List[SongInfo], config: BookConfig
    ) -> tuple:
        """Phase 1: Genere les pages systeme et compte leurs pages reelles.

        Returns:
            (temp_files, system_page_count)
        """
        temp_files = []
        system_page_count = 0

        if config.include_cover:
            cover_path = self._generate_cover(config, songs)
            temp_files.append(cover_path)
            cover_pages = self._count_pdf_pages(cover_path)
            system_page_count += cover_pages
            print(f"Page de garde generee ({cover_pages} page(s))")

        if config.include_toc:
            self._estimate_start_pages(songs, config)
            toc_path = self._generate_toc(songs, config)
            temp_files.append(toc_path)
            toc_pages = self._count_pdf_pages(toc_path)
            system_page_count += toc_pages
            print(f"Table des matieres generee ({toc_pages} page(s))")

        index_generators = [
            (config.include_index_title, self._generate_index_by_title, "titre"),
            (config.include_index_artist, self._generate_index_by_artist, "artiste"),
            (config.include_index_genre, self._generate_index_by_genre, "genre"),
        ]
        for enabled, gen_fn, label in index_generators:
            if enabled:
                self._estimate_start_pages(songs, config)
                idx_path = gen_fn(songs, config)
                temp_files.append(idx_path)
                idx_pages = self._count_pdf_pages(idx_path)
                system_page_count += idx_pages
                print(f"Index par {label} genere ({idx_pages} page(s))")

        return temp_files, system_page_count

    def _compute_song_start_pages(
        self, songs: List[SongInfo], system_page_count: int
    ):
        """Phase 2: Calcule les vraies pages de depart des morceaux."""
        print(f"\nPages systeme: {system_page_count}")
        current_page = system_page_count + 1
        for song in songs:
            song.start_page = current_page
            if song.pdf_path and os.path.exists(song.pdf_path):
                actual_pages = self._count_pdf_pages(song.pdf_path)
                song.pages = actual_pages
            else:
                actual_pages = song.pages or 1
            current_page += actual_pages
            print(f"  {song.title}: page {song.start_page} ({actual_pages} page(s))")

    def _regenerate_system_pages(
        self, temp_files: List[str], songs: List[SongInfo],
        config: BookConfig
    ) -> List[str]:
        """Phase 3: Regenere TOC et Index avec les bons numeros de page."""
        updated = []
        idx = 0

        if config.include_cover:
            updated.append(temp_files[idx])
            idx += 1

        regen_list = [
            (config.include_toc, self._generate_toc, "Table des matieres"),
            (config.include_index_title, self._generate_index_by_title, "Index par titre"),
            (config.include_index_artist, self._generate_index_by_artist, "Index par artiste"),
            (config.include_index_genre, self._generate_index_by_genre, "Index par genre"),
        ]
        for enabled, gen_fn, label in regen_list:
            if enabled:
                old_file = temp_files[idx]
                if os.path.exists(old_file):
                    os.remove(old_file)
                new_path = gen_fn(songs, config)
                updated.append(new_path)
                idx += 1
                print(f"{label} regenere avec pagination correcte")

        return updated

    def _merge_and_finalize(
        self, temp_files: List[str], songs: List[SongInfo],
        config: BookConfig
    ) -> str:
        """Phase 4: Fusionne et ecrit le PDF final."""
        print(f"\nFusion des {len(songs)} morceaux...")
        songs_with_pdf = [s for s in songs if s.pdf_path and Path(s.pdf_path).exists()]
        missing = len(songs) - len(songs_with_pdf)
        if missing > 0:
            print(f"   {missing} morceaux sans PDF (ignores)")

        output_filename = self._get_output_filename(config, len(songs))
        output_path = os.path.join(self.output_dir, output_filename)

        self._merge_all(temp_files, songs_with_pdf, output_path, config)
        print(f"\nPDF genere: {output_path}")
        return output_path

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
    # METHODES UTILITAIRES
    # =========================================================================

    @staticmethod
    def _song_model_to_info(song) -> SongInfo:
        """Convertit un modele Song SQLAlchemy en SongInfo."""
        return SongInfo(
            id=song.id,
            title=song.title,
            artist=song.artist or "",
            pdf_path=song.pdf_path,
            pages=song.pages or 1,
            instruments=json.loads(song.instruments) if song.instruments else [],
            source=song.source,
            type=song.type,
            genre=song.genre
        )

    def generate_from_book_id(self, book_id: int) -> str:
        """Genere un PDF a partir d'un book en base de donnees."""
        from app import app, db
        from models.book import Book

        with app.app_context():
            book = Book.query.get(book_id)
            if not book:
                raise ValueError(f"Book ID {book_id} non trouve")

            songs_data = [
                self._song_model_to_info(bs.song)
                for bs in sorted(book.book_songs, key=lambda x: x.position)
            ]

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

    def _load_songs_from_ids(self, song_ids: List[int]) -> List[SongInfo]:
        """Charge les SongInfo depuis la BDD a partir d'IDs."""
        from models.song import Song

        songs_data = []
        for song_id in song_ids:
            song = Song.query.get(song_id)
            if song:
                songs_data.append(self._song_model_to_info(song))
        return songs_data

    def generate_from_song_ids(
        self, song_ids: List[int], config: BookConfig = None, **kwargs
    ) -> str:
        """Genere un PDF a partir d'une liste d'IDs de morceaux.

        Args:
            song_ids: Liste des IDs de morceaux
            config: BookConfig (prefere). Si None, construit depuis kwargs.
            **kwargs: Parametres legacy (title, instrument, include_cover, etc.)
        """
        from app import app

        if config is None:
            # Compatibilite legacy: construire BookConfig depuis kwargs
            # Mapping des noms legacy -> noms BookConfig
            kw = dict(kwargs)
            if 'include_index' in kw:
                kw.setdefault('include_index_title', kw.pop('include_index'))
            config = BookConfig(**{
                k: kw[k] for k in kw if k in BookConfig.__dataclass_fields__
            })

        with app.app_context():
            songs_data = self._load_songs_from_ids(song_ids)
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
