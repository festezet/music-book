"""
Book Configuration Panel - Step 2: Configure TOC, indexes, page numbering
"""
import customtkinter as ctk
from typing import Callable, Dict, Any


class BookConfigPanel(ctk.CTkFrame):
    """Step 2: Book configuration - TOC, indexes, page numbers"""

    def __init__(self, parent, on_next: Callable, on_prev: Callable, get_config: Callable):
        super().__init__(parent, fg_color="transparent")

        self.on_next = on_next
        self.on_prev = on_prev
        self.get_config = get_config

        # Configuration variables
        self.config = {
            'title': ctk.StringVar(value="Mon Music Book"),
            'instrument': ctk.StringVar(value="guitar"),
            # Cover page
            'include_cover': ctk.BooleanVar(value=True),
            # Table of contents
            'include_toc': ctk.BooleanVar(value=True),
            # Index options
            'include_index_title': ctk.BooleanVar(value=True),
            'include_index_artist': ctk.BooleanVar(value=False),
            'include_index_genre': ctk.BooleanVar(value=False),
            # Page numbering
            'page_numbers': ctk.BooleanVar(value=True),
            'page_number_position': ctk.StringVar(value="center"),  # left, center, right
        }

        self._create_widgets()

    def _create_widgets(self):
        """Create panel UI"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # === Header ===
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))

        ctk.CTkLabel(
            header,
            text=" Configuration du Book",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        # Navigation buttons
        nav_frame = ctk.CTkFrame(header, fg_color="transparent")
        nav_frame.pack(side="right")

        ctk.CTkButton(
            nav_frame,
            text="<- Précédent",
            width=100,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.on_prev
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            nav_frame,
            text="Suivant ->",
            width=100,
            command=self.on_next
        ).pack(side="left", padx=5)

        # === Content ===
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # --- Cover Page Section ---
        self._create_section(content, " Page de garde", self._create_cover_options)

        # --- Table of Contents Section ---
        self._create_section(content, " Table des matières", self._create_toc_options)

        # --- Index Section ---
        self._create_section(content, " Index alphabétiques", self._create_index_options)

        # --- Page Numbering Section ---
        self._create_section(content, " Numérotation des pages", self._create_page_number_options)

    def _create_section(self, parent, title: str, content_func: Callable):
        """Create a configuration section"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.pack(fill="x", pady=10, padx=5)

        # Section title
        ctk.CTkLabel(
            frame,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(12, 8))

        # Separator
        ctk.CTkFrame(frame, height=1, fg_color=("#e5e7eb", "#374151")).pack(
            fill="x", padx=15, pady=(0, 10)
        )

        # Content
        content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=(0, 15))
        content_func(content_frame)

    def _create_cover_options(self, parent):
        """Create cover page options"""
        ctk.CTkCheckBox(
            parent,
            text="Inclure une page de garde",
            variable=self.config['include_cover']
        ).pack(anchor="w", pady=2)

        ctk.CTkLabel(
            parent,
            text="La page de garde affiche le titre, l'instrument, le nombre de morceaux et la date.",
            font=ctk.CTkFont(size=11),
            text_color=("#6b7280", "#9ca3af")
        ).pack(anchor="w", padx=25, pady=(0, 5))

    def _create_toc_options(self, parent):
        """Create table of contents options"""
        ctk.CTkCheckBox(
            parent,
            text="Inclure une table des matières",
            variable=self.config['include_toc']
        ).pack(anchor="w", pady=2)

        ctk.CTkLabel(
            parent,
            text="Liste les morceaux dans l'ordre du book avec numéros de page tabulés à droite.",
            font=ctk.CTkFont(size=11),
            text_color=("#6b7280", "#9ca3af")
        ).pack(anchor="w", padx=25, pady=(0, 5))

    def _create_index_options(self, parent):
        """Create index options"""
        ctk.CTkLabel(
            parent,
            text="Sélectionnez les index à inclure (après la table des matières):",
            font=ctk.CTkFont(size=12)
        ).pack(anchor="w", pady=(0, 10))

        # Index by title
        ctk.CTkCheckBox(
            parent,
            text="Index par titre (A-Z)",
            variable=self.config['include_index_title']
        ).pack(anchor="w", pady=2, padx=10)

        # Index by artist
        ctk.CTkCheckBox(
            parent,
            text="Index par artiste (A-Z)",
            variable=self.config['include_index_artist']
        ).pack(anchor="w", pady=2, padx=10)

        # Index by genre
        ctk.CTkCheckBox(
            parent,
            text="Index par genre",
            variable=self.config['include_index_genre']
        ).pack(anchor="w", pady=2, padx=10)

        ctk.CTkLabel(
            parent,
            text="Les numéros de page sont alignés à droite avec pointillés.",
            font=ctk.CTkFont(size=11),
            text_color=("#6b7280", "#9ca3af")
        ).pack(anchor="w", padx=10, pady=(10, 0))

    def _create_page_number_options(self, parent):
        """Create page numbering options"""
        # Enable/disable
        ctk.CTkCheckBox(
            parent,
            text="Afficher les numéros de page",
            variable=self.config['page_numbers']
        ).pack(anchor="w", pady=2)

        # Position
        pos_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pos_frame.pack(anchor="w", padx=25, pady=10)

        ctk.CTkLabel(pos_frame, text="Position:").pack(side="left", padx=(0, 10))

        for text, value in [("Gauche", "left"), ("Centre", "center"), ("Droite", "right")]:
            ctk.CTkRadioButton(
                pos_frame,
                text=text,
                variable=self.config['page_number_position'],
                value=value
            ).pack(side="left", padx=10)

    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration as dictionary"""
        return {
            'title': self.config['title'].get(),
            'instrument': self.config['instrument'].get(),
            'include_cover': self.config['include_cover'].get(),
            'include_toc': self.config['include_toc'].get(),
            'include_index_title': self.config['include_index_title'].get(),
            'include_index_artist': self.config['include_index_artist'].get(),
            'include_index_genre': self.config['include_index_genre'].get(),
            'page_numbers': self.config['page_numbers'].get(),
            'page_number_position': self.config['page_number_position'].get(),
        }

    def set_configuration(self, config: Dict[str, Any]):
        """Set configuration from dictionary"""
        for key, var in self.config.items():
            if key in config:
                var.set(config[key])
