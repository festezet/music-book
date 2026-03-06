"""
Export Options Panel - Step 3: PDF export configuration
"""
import customtkinter as ctk
from typing import Callable, Dict, Any


class ExportOptionsPanel(ctk.CTkFrame):
    """Step 3: PDF export options - format, orientation, margins"""

    def __init__(self, parent, on_next: Callable, on_prev: Callable, get_config: Callable):
        super().__init__(parent, fg_color="transparent")

        self.on_next = on_next
        self.on_prev = on_prev
        self.get_config = get_config

        # Export configuration variables
        self.export_config = {
            # Page format
            'page_format': ctk.StringVar(value="A4"),
            'orientation': ctk.StringVar(value="portrait"),
            # Margins (in mm)
            'margin_top': ctk.StringVar(value="20"),
            'margin_bottom': ctk.StringVar(value="20"),
            'margin_left': ctk.StringVar(value="15"),
            'margin_right': ctk.StringVar(value="15"),
            # Output
            'output_dir': ctk.StringVar(value="/data/projects/music-book/data/generated"),
            'filename_pattern': ctk.StringVar(value="{title}_{instrument}_{date}"),
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
            text=" Options d'export PDF",
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
            text="Générer ->",
            width=100,
            fg_color="#16a34a",
            hover_color="#15803d",
            command=self.on_next
        ).pack(side="left", padx=5)

        # === Content ===
        content = ctk.CTkScrollableFrame(self)
        content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        # --- Page Format Section ---
        self._create_section(content, " Format de page", self._create_format_options)

        # --- Margins Section ---
        self._create_section(content, " Marges", self._create_margin_options)

        # --- Output Section ---
        self._create_section(content, " Fichier de sortie", self._create_output_options)

        # --- Preview Section ---
        self._create_section(content, " Aperçu", self._create_preview)

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

    def _create_format_options(self, parent):
        """Create page format options"""
        # Format row
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        ctk.CTkLabel(row1, text="Format:", width=100, anchor="w").pack(side="left")

        for text, value in [("A4", "A4"), ("Letter", "LETTER"), ("A5", "A5")]:
            ctk.CTkRadioButton(
                row1,
                text=text,
                variable=self.export_config['page_format'],
                value=value
            ).pack(side="left", padx=15)

        # Orientation row
        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", pady=10)

        ctk.CTkLabel(row2, text="Orientation:", width=100, anchor="w").pack(side="left")

        for text, value in [("Portrait", "portrait"), ("Paysage", "landscape")]:
            ctk.CTkRadioButton(
                row2,
                text=text,
                variable=self.export_config['orientation'],
                value=value
            ).pack(side="left", padx=15)

    def _create_margin_options(self, parent):
        """Create margin options"""
        margins_frame = ctk.CTkFrame(parent, fg_color="transparent")
        margins_frame.pack(fill="x")

        # Grid layout for margins
        margins = [
            ("Haut:", 'margin_top', 0, 0),
            ("Bas:", 'margin_bottom', 0, 2),
            ("Gauche:", 'margin_left', 1, 0),
            ("Droite:", 'margin_right', 1, 2),
        ]

        for label, key, row, col in margins:
            ctk.CTkLabel(
                margins_frame,
                text=label,
                width=60,
                anchor="e"
            ).grid(row=row, column=col, padx=5, pady=5)

            entry_frame = ctk.CTkFrame(margins_frame, fg_color="transparent")
            entry_frame.grid(row=row, column=col+1, padx=5, pady=5)

            ctk.CTkEntry(
                entry_frame,
                textvariable=self.export_config[key],
                width=60
            ).pack(side="left")

            ctk.CTkLabel(entry_frame, text="mm").pack(side="left", padx=5)

        # Preset buttons
        preset_frame = ctk.CTkFrame(parent, fg_color="transparent")
        preset_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(preset_frame, text="Préréglages:").pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            preset_frame,
            text="Standard",
            width=80,
            height=28,
            command=lambda: self._apply_margin_preset("standard")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            preset_frame,
            text="Impression",
            width=80,
            height=28,
            command=lambda: self._apply_margin_preset("print")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            preset_frame,
            text="Compact",
            width=80,
            height=28,
            command=lambda: self._apply_margin_preset("compact")
        ).pack(side="left", padx=5)

    def _apply_margin_preset(self, preset: str):
        """Apply margin preset"""
        presets = {
            "standard": {"top": "20", "bottom": "20", "left": "15", "right": "15"},
            "print": {"top": "25", "bottom": "25", "left": "25", "right": "15"},
            "compact": {"top": "10", "bottom": "10", "left": "10", "right": "10"},
        }

        if preset in presets:
            p = presets[preset]
            self.export_config['margin_top'].set(p['top'])
            self.export_config['margin_bottom'].set(p['bottom'])
            self.export_config['margin_left'].set(p['left'])
            self.export_config['margin_right'].set(p['right'])

    def _create_output_options(self, parent):
        """Create output file options"""
        # Filename pattern
        row1 = ctk.CTkFrame(parent, fg_color="transparent")
        row1.pack(fill="x", pady=5)

        ctk.CTkLabel(row1, text="Nom du fichier:", width=120, anchor="w").pack(side="left")
        ctk.CTkEntry(
            row1,
            textvariable=self.export_config['filename_pattern'],
            width=300
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            parent,
            text="Variables: {title}, {instrument}, {date}, {count}",
            font=ctk.CTkFont(size=11),
            text_color=("#6b7280", "#9ca3af")
        ).pack(anchor="w", padx=120, pady=(0, 10))

        # Output directory
        row2 = ctk.CTkFrame(parent, fg_color="transparent")
        row2.pack(fill="x", pady=5)

        ctk.CTkLabel(row2, text="Dossier de sortie:", width=120, anchor="w").pack(side="left")

        self.dir_entry = ctk.CTkEntry(
            row2,
            textvariable=self.export_config['output_dir'],
            width=350
        )
        self.dir_entry.pack(side="left", padx=10)

        ctk.CTkButton(
            row2,
            text="Parcourir...",
            width=100,
            command=self._browse_output_dir
        ).pack(side="left", padx=5)

    def _browse_output_dir(self):
        """Open directory browser"""
        from tkinter import filedialog
        directory = filedialog.askdirectory()
        if directory:
            self.export_config['output_dir'].set(directory)

    def _create_preview(self, parent):
        """Create preview section"""
        preview_frame = ctk.CTkFrame(parent, corner_radius=8, fg_color=("#f3f4f6", "#1f2937"))
        preview_frame.pack(fill="x", pady=5)

        self.preview_text = ctk.CTkLabel(
            preview_frame,
            text="Aperçu du fichier généré...",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w"
        )
        self.preview_text.pack(fill="x", padx=15, pady=15)

        # Update preview when config changes
        for var in self.export_config.values():
            var.trace("w", lambda *args: self._update_preview())

        self._update_preview()

    def _update_preview(self):
        """Update the preview text"""
        config = self.get_export_config()

        filename = config['filename_pattern']
        filename = filename.replace("{title}", "Mon_Music_Book")
        filename = filename.replace("{instrument}", config['page_format'])
        filename = filename.replace("{date}", "2025-12-21")
        filename = filename.replace("{count}", "8")

        output_dir = config['output_dir'] or "data/generated/"

        preview = f"""Fichier: {filename}.pdf
Dossier: {output_dir}
Format: {config['page_format']} ({config['orientation']})
Marges: {config['margin_top']}mm / {config['margin_bottom']}mm / {config['margin_left']}mm / {config['margin_right']}mm"""

        self.preview_text.configure(text=preview)

    def get_export_config(self) -> Dict[str, Any]:
        """Get current export configuration"""
        return {
            'page_format': self.export_config['page_format'].get(),
            'orientation': self.export_config['orientation'].get(),
            'margin_top': int(self.export_config['margin_top'].get() or 20),
            'margin_bottom': int(self.export_config['margin_bottom'].get() or 20),
            'margin_left': int(self.export_config['margin_left'].get() or 15),
            'margin_right': int(self.export_config['margin_right'].get() or 15),
            'output_dir': self.export_config['output_dir'].get(),
            'filename_pattern': self.export_config['filename_pattern'].get(),
        }

    def set_export_config(self, config: Dict[str, Any]):
        """Set export configuration"""
        for key, var in self.export_config.items():
            if key in config:
                var.set(str(config[key]))
