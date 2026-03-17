# Music Book Generator - Specification Technique
> Version: 2.0 | Date: 2026-03-13 | Projet: PRJ-XXX (music-book)

---

## 1. Vision & Contexte

### 1.1 Probleme

Un musicien qui joue de plusieurs instruments (guitare, basse, violon) accumule des partitions PDF telecharges depuis differentes sources (Ultimate Guitar, Songsterr, La Boite a chansons). Ces fichiers sont en vrac, sans organisation, et il est impossible de les assembler rapidement en un livre structure avec table des matieres, pagination coherente et index.

Music Book Generator resout ce probleme en offrant un catalogue centralise de partitions avec metadonnees, et un outil de construction de livres PDF professionnels avec generation automatique de pages systeme (couverture, TOC, index).

### 1.2 Utilisateurs

| Profil | Objectif | Usage |
|--------|----------|-------|
| Musicien multi-instrumentiste | Organiser ses partitions et generer des livres PDF imprimes | Hebdomadaire |
| Musicien en repetition | Consulter rapidement un morceau dans un book genere | Quotidien |

### 1.3 Criteres de succes

- [x] Un PDF genere contient couverture, table des matieres, morceaux fusionnes et index avec pagination correcte
- [x] L'import depuis un dossier de PDFs detecte automatiquement titre, artiste, source et instrument
- [x] Le catalogue permet recherche et filtrage par instrument, genre, artiste, difficulte
- [x] Le workflow GUI genere un PDF complet en moins de 10 secondes pour 50 morceaux
- [ ] 3 versions (guitare, basse, violon) generees depuis un seul workflow

---

## 2. Stack Technique

| Couche | Technologie | Version | Justification |
|--------|------------|---------|---------------|
| Backend | Python 3 + Flask | Flask 3.0.0 | Framework leger, suffisant pour API REST + rendu templates |
| ORM | SQLAlchemy | 2.0.23 | ORM standard Python, integration Flask-SQLAlchemy 3.1.1 |
| Base de donnees | SQLite | 3.x (builtin) | Base locale, zero config, fichier unique |
| PDF generation | reportlab | 4.0.7 | Creation de pages systeme (couverture, TOC, index) |
| PDF manipulation | PyPDF2 + pypdf | PyPDF2 3.0.1, pypdf 3.17.4 | Lecture, fusion, overlay de PDFs existants |
| PDF complementaire | pdfrw | 0.4 | Manipulation bas-niveau PDF |
| Images | Pillow | 10.1.0 | Traitement images pour couvertures |
| GUI Desktop | CustomTkinter | latest | Interface workflow 4 etapes |
| GUI Desktop (legacy) | Tkinter | builtin | Interface simple catalogue + generation |
| Frontend Web | HTML5/CSS3 + JavaScript vanilla | - | Pas de framework, simplicite |
| Templates | Jinja2 | (via Flask) | Rendu HTML cote serveur |
| CORS | Flask-CORS | 4.0.0 | Autorise appels cross-origin |

### 2.1 Dependances externes

**Fichier** : `/data/projects/music-book/requirements.txt`

```
Flask==3.0.0
Flask-CORS==4.0.0
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1
pypdf==3.17.4
PyPDF2==3.0.1
reportlab==4.0.7
pdfrw==0.4
Pillow==10.1.0
pdf2image==1.16.3
customtkinter
```

Aucun service Docker requis. Aucune API externe.

---

## 3. Architecture

### 3.1 Vue Contexte (C4 Level 1)

```
[Musicien] --> [Music Book Generator]
                     |
                [Fichiers PDF locaux]
                (partitions telechargees depuis UG, Songsterr, BAC)
```

Le systeme est entierement local. Pas de serveur distant, pas d'authentification.

### 3.2 Vue Container (C4 Level 2)

```
[Interface Web]                    [Interface GUI Workflow]         [CLI]
  (Flask + Jinja2 + JS)             (CustomTkinter)                (argparse)
         |                                |                          |
         +------------ [Flask Backend] --------------------------------+
                            |
                   [SQLAlchemy ORM]
                            |
                   [SQLite: catalog.db]
                            |
                   [PDF Generator Service]
                       |          |
              [reportlab]     [PyPDF2/PdfMerger]
              (pages systeme)  (fusion + overlay)
                       |
              [Fichiers PDF generes]
```

### 3.3 Structure du projet

```
music-book/
├── backend/
│   ├── app.py                          # Point d'entree Flask, routes HTML
│   ├── config.py                       # Configuration (port, chemins, instruments)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── song.py                     # Modele Song (SQLAlchemy)
│   │   ├── book.py                     # Modele Book (SQLAlchemy)
│   │   └── book_song.py               # Table association Book<->Song
│   ├── services/
│   │   └── pdf_generator.py           # MusicBookGenerator (reportlab + PyPDF2)
│   └── api/
│       ├── __init__.py
│       └── routes.py                   # REST API (Blueprint /api)
├── frontend/
│   ├── templates/
│   │   ├── base.html                   # Template de base Jinja2 (navbar)
│   │   ├── catalog.html                # Page catalogue (grille + modals)
│   │   ├── book_builder.html           # Page construction book (drag & drop)
│   │   ├── import.html                 # Page import PDF
│   │   └── settings.html               # Page parametres
│   └── static/
│       ├── css/
│       │   └── style.css               # Styles (CSS variables, responsive grid)
│       └── js/
│           ├── app.js                  # Utilitaires globaux (apiRequest, notifications)
│           ├── catalog.js              # Logique catalogue (CRUD, recherche, filtres)
│           └── book_builder.js         # Logique book builder (drag & drop, modals)
├── src/
│   └── widgets/                        # Widgets CustomTkinter (GUI workflow)
│       ├── __init__.py                 # Exports publics
│       ├── song_library.py            # Etape 1: Selection morceaux (widget recycling)
│       ├── book_config.py             # Etape 2: Configuration book
│       ├── export_options.py          # Etape 3: Options export (format, marges)
│       ├── generation.py              # Etape 4: Generation PDF (thread background)
│       ├── book_list.py               # Panneau liste des books sauvegardes
│       ├── song_manager.py            # Dialog gestion bibliotheque
│       └── workflow_sidebar.py        # Barre navigation 4 etapes
├── scripts/
│   ├── batch_import.py                 # Import masse avec detection metadonnees
│   ├── import_chords_folder.py         # Import avec regex compiles
│   ├── extract_metadata_from_pdf.py    # Extraction tonalite/difficulte depuis PDF
│   └── generate_dummy_catalog.py       # Generation donnees de test (31 morceaux)
├── data/
│   ├── catalog.db                      # Base SQLite (gitignore)
│   ├── pdfs/
│   │   ├── guitar/                     # PDF partitions guitare
│   │   ├── bass/                       # PDF partitions basse
│   │   └── violin/                     # PDF partitions violon
│   ├── generated/                      # PDF books generes
│   ├── imports/                        # Upload temporaire
│   ├── exports/                        # Exports catalogue
│   └── backups/                        # Backups automatiques DB
├── cli.py                              # Interface ligne de commande
├── db_backup.py                        # Backup DB avec rotation (10 derniers)
├── music_book_gui.py                   # GUI Tkinter (legacy)
├── workflow_gui.py                     # GUI CustomTkinter workflow 4 etapes
├── start.sh                            # Lancement serveur web
├── lancer_music_book.sh                # Lancement GUI Tkinter
├── lancer_workflow.sh                  # Lancement GUI workflow
├── requirements.txt
└── README.md
```

### 3.4 Flux de donnees

```
Flux 1 - Import :
  [Dossier PDF] → [batch_import.py: parse filename] → [detect source/type/instrument/genre]
                → [copie vers data/pdfs/{instrument}/] → [INSERT songs] → [catalog.db]

Flux 2 - Construction book (Web) :
  [Catalogue filtré] → [Drag & Drop] → [POST /api/books/<id>/add_song]
                     → [INSERT book_songs avec position] → [catalog.db]

Flux 3 - Construction book (GUI) :
  [SongLibraryPanel: selection + filtres] → [BookConfigPanel: options]
                     → [ExportOptionsPanel: format/marges] → [GenerationPanel]

Flux 4 - Generation PDF :
  [MusicBookGenerator.generate(songs, config)]
    → Phase 1: reportlab genere pages systeme (cover, TOC, index) → PDF temporaires
    → Phase 2: Calcul numeros de pages reels (comptage PDF sources)
    → Phase 3: Regeneration TOC/index avec pagination correcte
    → Phase 4: PdfMerger fusionne [systeme + morceaux] → PDF temporaire
    → Phase 5: PdfWriter ajoute overlays (numeros page + headers titre/artiste)
    → [PDF final dans data/generated/]

Flux 5 - Backup :
  [db_backup.py] → [copie catalog.db] → [data/backups/catalog_YYYYMMDD_HHMMSS.db.bak]
                 → [rotation: supprime au-dela de 10 fichiers]
```

---

## 4. Modele de Donnees

### 4.1 Schema conceptuel

| Entite | Description | Relations |
|--------|-------------|-----------|
| Song | Un morceau de musique avec ses metadonnees et chemin vers le PDF source | 1 Song → N BookSong |
| Book | Un livre de partitions configure (titre, instrument, options) | 1 Book → N BookSong |
| BookSong | Association ordonnee entre un Book et un Song | N:1 vers Book, N:1 vers Song |

```
[Song] 1 ←——→ N [BookSong] N ←——→ 1 [Book]
               (position ordonnee)
```

Un morceau peut apparaitre dans plusieurs books. Un book contient N morceaux ordonnes via `position`.

### 4.2 Schema SQL

Les tables sont creees par SQLAlchemy via `db.create_all()` dans `backend/app.py`. Voici le schema equivalent :

```sql
-- Table: songs
-- Source: backend/models/song.py
CREATE TABLE IF NOT EXISTS songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    key VARCHAR(10),                    -- Tonalite (C, Dm, G7, etc.)
    tempo INTEGER,                      -- BPM
    genre VARCHAR(100),                 -- Rock, Chanson Francaise, Pop, etc.
    difficulty VARCHAR(20),             -- 'easy', 'medium', 'advanced'
    instruments TEXT,                    -- JSON array: '["guitar", "bass"]'
    tags TEXT,                          -- JSON array: '["acoustic", "fingerstyle"]'
    pdf_path VARCHAR(500) NOT NULL,     -- Chemin absolu vers le PDF source
    pages INTEGER,                      -- Nombre de pages du PDF
    source VARCHAR(50),                 -- 'ultimate_guitar', 'songsterr', 'boite_chansons'
    type VARCHAR(20),                   -- 'chords', 'tab'
    youtube_url VARCHAR(255),           -- Lien YouTube optionnel
    tuning VARCHAR(50),                 -- Accordage (E A D G B E, Drop D, etc.)
    notes TEXT,                         -- Notes libres
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherche rapide
CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title);
CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist);
CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre);
CREATE INDEX IF NOT EXISTS idx_songs_difficulty ON songs(difficulty);
CREATE INDEX IF NOT EXISTS idx_songs_source ON songs(source);

-- Note: updated_at est gere par SQLAlchemy (onupdate=datetime.utcnow)
-- Equivalent trigger SQLite pour usage hors ORM :
CREATE TRIGGER IF NOT EXISTS update_songs_timestamp
    AFTER UPDATE ON songs
    FOR EACH ROW
    BEGIN
        UPDATE songs SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;


-- Table: books
-- Source: backend/models/book.py
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    instrument VARCHAR(50) NOT NULL,     -- 'guitar', 'bass', 'violin'
    format VARCHAR(20) DEFAULT 'A4',     -- 'A4', 'LETTER', 'A5'
    orientation VARCHAR(20) DEFAULT 'portrait',  -- 'portrait', 'landscape'
    include_toc BOOLEAN DEFAULT 1,       -- Table des matieres
    include_index BOOLEAN DEFAULT 1,     -- Index alphabetique
    include_cover BOOLEAN DEFAULT 1,     -- Page de garde
    pdf_path VARCHAR(500),               -- Chemin vers le dernier PDF genere (nullable)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_books_instrument ON books(instrument);
CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);


-- Table: book_songs (association N:N ordonnee)
-- Source: backend/models/book_song.py
CREATE TABLE IF NOT EXISTS book_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    position INTEGER NOT NULL,           -- Ordre dans le book (1, 2, 3...)
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_book_songs_book_id ON book_songs(book_id);
CREATE INDEX IF NOT EXISTS idx_book_songs_song_id ON book_songs(song_id);
CREATE INDEX IF NOT EXISTS idx_book_songs_position ON book_songs(book_id, position);
```

### 4.3 Stockage JSON dans les colonnes TEXT

Les colonnes `instruments` et `tags` de la table `songs` stockent des tableaux JSON serialises en texte :

```python
# Ecriture (backend/models/song.py, Song.from_dict)
instruments = json.dumps(["guitar", "bass"])   # → '["guitar", "bass"]'
tags = json.dumps(["acoustic", "fingerstyle"]) # → '["acoustic", "fingerstyle"]'

# Lecture (backend/models/song.py, Song.to_dict)
instruments = json.loads(self.instruments) if self.instruments else []

# Filtrage (backend/api/routes.py)
query = query.filter(Song.instruments.contains(f'"{instrument}"'))
```

### 4.4 Valeurs possibles

| Champ | Valeurs | Source |
|-------|---------|--------|
| `songs.source` | `ultimate_guitar`, `songsterr`, `boite_chansons` | Detection automatique par `batch_import.py` |
| `songs.type` | `chords`, `tab` | Detection automatique par filename |
| `songs.difficulty` | `easy`, `medium`, `advanced` | Config: `backend/config.py` DIFFICULTY_LEVELS |
| `books.instrument` | `guitar`, `bass`, `violin` | Config: `backend/config.py` INSTRUMENTS |
| `books.format` | `A4`, `LETTER`, `A5` | `pdf_generator.py` BookConfig |
| `books.orientation` | `portrait`, `landscape` | `pdf_generator.py` BookConfig |

### 4.5 Migrations

Pas de systeme de migration formalise. Les tables sont creees par `db.create_all()` au demarrage de l'application Flask (`backend/app.py` ligne 28).

Historique des changements de schema manuels :
- **2025-12-23** : Ajout de la colonne `pdf_path` a la table `books` (etait absente du modele initial, causait des erreurs silencieuses a la sauvegarde des books generes).

---

## 5. Features (Exigences Fonctionnelles)

### F-001: Catalogue de morceaux (P1)

**User story :** En tant que musicien, je veux cataloguer mes partitions PDF avec leurs metadonnees, afin de les retrouver et les filtrer facilement.

**Criteres d'acceptation :**
- [x] CRUD complet sur les morceaux (API REST + interface web + GUI)
- [x] Metadonnees : titre, artiste, tonalite, tempo, genre, difficulte, instruments, tags, source, type, accordage, URL YouTube, notes
- [x] Filtrage par instrument, difficulte, artiste, genre, source
- [x] Recherche texte sur titre et artiste (ILIKE)
- [x] Affichage en grille responsive (CSS Grid, minmax 280px)

**Implementation :**
- API : `backend/api/routes.py` (endpoints `/api/catalog`)
- Modele : `backend/models/song.py` (classe `Song`)
- Web : `frontend/templates/catalog.html` + `frontend/static/js/catalog.js`
- GUI : `src/widgets/song_library.py` (classe `SongLibraryPanel`)

**Cas limites :**
- PDF sans metadonnees : les champs optionnels sont nullable, seuls `title` et `pdf_path` sont requis
- Instruments stockes en JSON : le filtrage utilise `LIKE '%"guitar"%'` (fonctionne pour les 3 instruments definis)

---

### F-002: Import en masse de PDFs (P1)

**User story :** En tant que musicien, je veux importer un dossier entier de partitions PDF, afin de peupler le catalogue automatiquement sans saisie manuelle.

**Criteres d'acceptation :**
- [x] Detection automatique du titre et de l'artiste depuis le nom de fichier
- [x] Support des 3 formats source : Ultimate Guitar, Songsterr, La Boite a chansons
- [x] Detection du type (chords/tab) et de l'instrument (guitar/bass/violin)
- [x] Detection du genre par dictionnaire d'artistes connus (chanson francaise, rock)
- [x] Detection des doublons (meme titre + artiste + instrument)
- [x] Mode dry-run pour simulation
- [x] Copie des PDFs vers `data/pdfs/{instrument}/`

**Implementation :**
- Script principal : `scripts/batch_import.py` (fonction `batch_import()`)
- Parseurs de noms de fichiers (3 fonctions) :
  ```python
  # scripts/batch_import.py

  # Pattern Ultimate Guitar:
  # "Title Chords (ver N) by Artisttabs @ Ultimate Guitar Archive.pdf"
  parse_ultimate_guitar_filename(filename)

  # Pattern Songsterr:
  # "Title Tab by Artist _ Songsterr Tabs with Rhythm.pdf"
  parse_songsterr_filename(filename)

  # Pattern Boite a chansons:
  # "Title - Artist - La Boite a chansons.pdf"
  parse_boite_chansons_filename(filename)
  ```
- Detection genre : dictionnaires `CHANSON_FRANCAISE_ARTISTS` et `OTHER_ARTISTS_GENRES` dans `batch_import.py`
- Import GUI multi-fichiers : `src/widgets/song_manager.py` (classe `SongManagerDialog`, methode d'import multi-PDF avec auto-detection)
- CLI : `cli.py import-folder <path> [--dry-run]`

**Cas limites :**
- Nom de fichier non reconnu : fallback utilise le nom complet comme titre, artiste vide
- PDF sans extension `.pdf` : ignore par le glob `*.pdf`
- Doublons : detection par titre + artiste + instrument (ILIKE), retourne status `skipped`

---

### F-003: Construction de books (P1)

**User story :** En tant que musicien, je veux selectionner et ordonner des morceaux pour creer un livre de partitions, afin de l'imprimer et l'utiliser en repetition.

**Criteres d'acceptation :**
- [x] Creation de book avec titre, instrument cible, options (couverture, TOC, index)
- [x] Ajout de morceaux avec verification de compatibilite instrument
- [x] Reordonnancement des morceaux (drag & drop web, boutons up/down GUI)
- [x] Suppression de morceaux du book
- [x] Preview table des matieres avant generation

**Implementation Web (drag & drop) :**
- Template : `frontend/templates/book_builder.html` (deux panneaux : catalogue filtre + book)
- JavaScript : `frontend/static/js/book_builder.js`
  ```javascript
  // Drag & Drop HTML5 API
  // frontend/static/js/book_builder.js

  function handleDragStart(e) {
      e.dataTransfer.setData('text/plain', e.target.dataset.songId);
      e.target.classList.add('dragging');
  }

  function handleDrop(e) {
      e.preventDefault();
      const songId = e.dataTransfer.getData('text/plain');
      addSongToBook(songId);  // POST /api/books/<id>/add_song
  }
  ```
- Verification instrument cote serveur : `routes.py`, `add_song_to_book()` verifie `song.has_instrument(book.instrument)` avant insertion

**Implementation GUI (workflow) :**
- Selection : `src/widgets/song_library.py` avec filtres (instrument, source, genre, artiste), tri (titre, artiste, genre, source), boutons ajouter/retirer/monter/descendre
- Configuration : `src/widgets/book_config.py` (couverture, TOC, index titre/artiste/genre, numerotation pages)
- Liste books : `src/widgets/book_list.py` avec highlight du book actif (bleu), clic droit pour renommer/supprimer

**Cas limites :**
- Ajout d'un morceau incompatible : retourne HTTP 400 avec message explicite
- Position automatique : `max(position) + 1` sur les `book_songs` du book
- Reordonnancement : `POST /api/books/<id>/reorder` avec tableau d'IDs ordonne

---

### F-004: Generation de PDF (P1)

**User story :** En tant que musicien, je veux generer un PDF complet a partir de mon book, afin d'obtenir un livre imprimable avec couverture, table des matieres et index.

**Criteres d'acceptation :**
- [x] Page de garde avec titre, instrument (icone), nombre de morceaux/pages, date
- [x] Table des matieres avec numeros de page corrects (generation deux passes)
- [x] Index alphabetique par titre (lettres A-Z avec regroupement)
- [x] Index par artiste (optionnel, avec morceaux groupes)
- [x] Index par genre (optionnel, avec morceaux groupes)
- [x] Fusion des PDF sources via PdfMerger
- [x] Overlay : numeros de page en pied, titre+artiste en en-tete pour chaque morceau
- [x] Support formats A4, Letter, A5 en portrait ou paysage
- [x] Marges configurables avec presets (standard, impression, compact)
- [x] Pattern de nom de fichier configurable avec variables

**Implementation :**
- Generateur : `backend/services/pdf_generator.py` (classe `MusicBookGenerator`)
- Dataclasses : `SongInfo` (donnees morceau) et `BookConfig` (configuration complete)

**Pipeline de generation (5 phases) :**

```python
# backend/services/pdf_generator.py - MusicBookGenerator.generate()

# PHASE 1: Generer pages systeme avec reportlab
#   _generate_cover()  → SimpleDocTemplate + Paragraph/Spacer
#   _generate_toc()    → Table avec colonnes [titre, page] alignees
#   _generate_index_by_title()   → Groupes par lettre A-Z
#   _generate_index_by_artist()  → Groupes par artiste
#   _generate_index_by_genre()   → Groupes par genre musical

# PHASE 2: Calculer les vrais numeros de page
#   Compter les pages reelles de chaque PDF source via PdfReader
#   song.start_page = system_page_count + cumul_pages_precedentes + 1

# PHASE 3: Regenerer TOC et index avec les bons numeros
#   Supprime les fichiers temporaires Phase 1
#   Regenere avec song.start_page corrige

# PHASE 4: Fusion via PdfMerger
#   merger.append(cover) + merger.append(toc) + merger.append(index)
#   + merger.append(song.pdf_path) pour chaque morceau

# PHASE 5: Overlay via PdfWriter + Canvas
#   Pour chaque page: cree un overlay transparent avec :
#     - Numero de page en bas (position configurable: left/center/right)
#     - Titre + Artiste + (N/M) en haut pour les pages de morceaux
#   page.merge_page(overlay) pour superposer
```

**Couleurs du theme :**
```python
PRIMARY_COLOR = HexColor("#2563eb")    # Bleu titres/liens
SECONDARY_COLOR = HexColor("#64748b")  # Gris sous-titres
TEXT_COLOR = HexColor("#1e293b")       # Noir texte
```

**Styles reportlab personnalises :**
- `BookTitle` : 36pt, bleu, centre (page de garde)
- `BookSubtitle` : 18pt, gris, centre
- `TOCTitle` : 24pt, bleu, centre
- `TOCEntry` : 12pt, indent 20pt, espacement 8pt
- `IndexTitle` : 24pt, bleu, centre

**Presets de marges (en mm) :**
| Preset | Haut | Bas | Gauche | Droite |
|--------|------|-----|--------|--------|
| Standard | 20 | 20 | 15 | 15 |
| Impression | 25 | 25 | 25 | 15 |
| Compact | 10 | 10 | 10 | 10 |

**Pattern de nom de fichier :**
- Defaut : `{title}_{instrument}_{date}.pdf`
- Variables : `{title}`, `{instrument}`, `{date}` (YYYY-MM-DD), `{count}` (nombre morceaux)

**Cas limites :**
- Morceau sans PDF source (fichier manquant) : ignore avec message console, les autres morceaux sont fusionnes normalement
- PDF source avec taille de page differente du format configure : l'overlay s'adapte a la taille reelle de chaque page (`page.mediabox.width/height`)
- Pagination deux passes : la premiere estimation utilise `(len(songs) // 20) + 1` pages pour la TOC, puis recalcule apres comptage reel

---

### F-005: Interface GUI Workflow (P2)

**User story :** En tant que musicien, je veux une interface desktop guidee etape par etape, afin de construire et generer mes books sans navigateur web.

**Criteres d'acceptation :**
- [x] 4 etapes visuelles dans une sidebar (Selection, Configuration, Export, Generation)
- [x] Performance : changement de book quasi-instantane (<0.2s pour 50+ morceaux)
- [x] Widget recycling pour zero latence (pool de widgets reutilisables)
- [x] Recherche et filtrage temps reel dans la bibliotheque
- [x] Generation PDF dans un thread background avec barre de progression
- [x] Ouverture du PDF et du dossier apres generation (xdg-open)
- [x] Renommage de books par clic droit
- [x] Highlight visuel du book actif (bleu)

**Implementation :**
- Point d'entree : `workflow_gui.py`
- Navigation : `src/widgets/workflow_sidebar.py` (4 noeuds avec indicateurs cercle)
  - Pending = gris, Current = bleu (#2563eb), Completed = vert (#10b981)
  - ConnectorLine entre chaque noeud, couleur dynamique selon etat

**Widget Recycling (performance critique) :**
```python
# src/widgets/song_library.py - SongLibraryPanel

MAX_DISPLAY = 50  # Nombre max de widgets affiches

# Structures O(1) pour lookups rapides
_selected_song_ids_set = set()    # Verification instant O(1)
_songs_by_id = {}                 # Dict index {id: song_data}

# Pool de widgets reutilisables
def _create_recyclable_item():
    """Cree un widget UNE SEULE FOIS, reutilise ensuite"""
    frame = ctk.CTkFrame(...)
    # ... boutons, labels
    return frame

def _update_widget_content(widget, song_data):
    """Met a jour le CONTENU sans recreer le widget"""
    widget.name_label.configure(text=song_data['title'])
    widget.artist_label.configure(text=song_data['artist'])
```

**Tri des morceaux :**
- Par titre (A-Z, Z-A)
- Par artiste (A-Z, Z-A) - tri par nom de famille (dernier mot)
- Par genre
- Par source
- "Ajouter tout" : tri par nom de famille artiste puis titre

---

### F-006: Backup automatique (P2)

**User story :** En tant que musicien, je veux que ma base de donnees soit sauvegardee automatiquement, afin de ne pas perdre mon catalogue en cas de probleme.

**Criteres d'acceptation :**
- [x] Backup du fichier `catalog.db` vers `data/backups/`
- [x] Nommage avec timestamp : `catalog_YYYYMMDD_HHMMSS.db.bak`
- [x] Rotation : garde les 10 derniers backups, supprime les plus anciens
- [x] Executable standalone : `python3 db_backup.py`

**Implementation :**
- Script : `db_backup.py` (racine du projet)
- Fonction principale : `backup_database()`
- Constantes : `MAX_BACKUPS = 10`, `DATA_DIR = Path(__file__).parent / "data"`
- Restauration : `cp data/backups/catalog_XXXXXXXX_XXXXXX.db.bak data/catalog.db`

---

### F-007: Interface CLI (P3)

**User story :** En tant que musicien/developpeur, je veux manipuler le catalogue depuis le terminal, afin de faire des operations rapides sans interface graphique.

**Criteres d'acceptation :**
- [x] `list-songs` avec filtres `--genre`, `--artist`, `--limit`
- [x] `list-books` avec compteur de morceaux par book
- [x] `import-folder <path>` avec `--dry-run`
- [x] `stats` : total partitions, livres, artistes, repartition par genre
- [x] `search <query>` : recherche titre + artiste (ILIKE, limite 50)

**Implementation :**
- Fichier : `cli.py` (racine du projet)
- Pattern : argparse avec subparsers, fonctions `cmd_*` par commande
- Contexte Flask : chaque commande utilise `with app.app_context():`

**Cas limites :**
- `import-folder` delegue a `batch_import.import_pdf_file()` (import dans scripts/)
- `--limit` par defaut 100 pour `list-songs`
- Affichage tabule avec troncature des champs longs (24/34/19 caracteres)

---

## 6. API / Interfaces

### 6.1 Endpoints REST

Blueprint enregistre dans `backend/app.py` : `app.register_blueprint(api_bp, url_prefix='/api')`

Fichier source : `backend/api/routes.py`

#### Catalogue

| Methode | Endpoint | Description | Statut |
|---------|----------|-------------|--------|
| `GET` | `/api/catalog` | Liste morceaux (filtres: `instrument`, `difficulty`, `artist`, `search`) | OK |
| `GET` | `/api/catalog/<id>` | Detail d'un morceau | OK |
| `POST` | `/api/catalog` | Creer un morceau (body JSON) | OK (201) |
| `PUT` | `/api/catalog/<id>` | Modifier metadonnees | OK |
| `DELETE` | `/api/catalog/<id>` | Supprimer un morceau | OK |

#### Books

| Methode | Endpoint | Description | Statut |
|---------|----------|-------------|--------|
| `GET` | `/api/books` | Liste des books (tri par created_at desc) | OK |
| `GET` | `/api/books/<id>` | Detail d'un book | OK |
| `POST` | `/api/books` | Creer un book (body JSON) | OK (201) |
| `PUT` | `/api/books/<id>` | Modifier un book | OK |
| `DELETE` | `/api/books/<id>` | Supprimer un book (cascade book_songs) | OK |

#### Book Songs

| Methode | Endpoint | Description | Statut |
|---------|----------|-------------|--------|
| `GET` | `/api/books/<id>/songs` | Morceaux du book (ordonnés par position) | OK |
| `POST` | `/api/books/<id>/add_song` | Ajouter un morceau (verifie instrument) | OK (201) |
| `DELETE` | `/api/books/<id>/remove_song/<song_id>` | Retirer un morceau | OK |
| `POST` | `/api/books/<id>/reorder` | Reordonner (body: `{"song_ids": [3,1,5]}`) | OK |

#### Generation & Preview

| Methode | Endpoint | Description | Statut |
|---------|----------|-------------|--------|
| `POST` | `/api/books/<id>/generate` | Generer PDF | **501 (non implemente via web API)** |
| `GET` | `/api/books/<id>/preview` | Preview TOC avec pagination estimee | OK |

#### Import & Export

| Methode | Endpoint | Description | Statut |
|---------|----------|-------------|--------|
| `POST` | `/api/import/pdf` | Upload PDF | **501 (non implemente)** |
| `GET` | `/api/export/catalog` | Export catalogue | **501 (non implemente)** |

### 6.2 Formats de requete/reponse

**POST /api/catalog** (creer un morceau) :
```json
{
    "title": "Hotel California",
    "artist": "Eagles",
    "key": "Bm",
    "tempo": 75,
    "genre": "Rock",
    "difficulty": "medium",
    "instruments": ["guitar", "bass"],
    "tags": ["classic", "acoustic"],
    "pdf_path": "/data/projects/music-book/data/pdfs/guitar/hotel_california.pdf",
    "pages": 3,
    "source": "ultimate_guitar",
    "type": "chords",
    "notes": "Intro fingerpicking"
}
```

**Reponse (to_dict) :**
```json
{
    "id": 1,
    "title": "Hotel California",
    "artist": "Eagles",
    "key": "Bm",
    "tempo": 75,
    "genre": "Rock",
    "difficulty": "medium",
    "instruments": ["guitar", "bass"],
    "tags": ["classic", "acoustic"],
    "pdf_path": "/data/projects/music-book/data/pdfs/guitar/hotel_california.pdf",
    "pages": 3,
    "source": "ultimate_guitar",
    "type": "chords",
    "youtube_url": null,
    "tuning": null,
    "notes": "Intro fingerpicking",
    "created_at": "2026-03-13T14:30:00",
    "updated_at": "2026-03-13T14:30:00"
}
```

**POST /api/books** (creer un book) :
```json
{
    "title": "Rock Classics",
    "instrument": "guitar",
    "format": "A4",
    "orientation": "portrait",
    "include_toc": true,
    "include_index": true,
    "include_cover": true
}
```

**POST /api/books/<id>/add_song** :
```json
{
    "song_id": 42
}
```

**Erreur 400 (instrument incompatible) :**
```json
{
    "error": "Song \"Hotel California\" is not compatible with violin"
}
```

**GET /api/books/<id>/preview** :
```json
{
    "book": { "id": 1, "title": "Rock Classics", "instrument": "guitar", "song_count": 5 },
    "toc": [
        { "title": "Hotel California", "artist": "Eagles", "page": 4, "pages": 3 },
        { "title": "Stairway to Heaven", "artist": "Led Zeppelin", "page": 7, "pages": 4 }
    ],
    "total_pages": 15
}
```

### 6.3 Interfaces CLI

```bash
# cli.py
python3 cli.py list-songs [--genre GENRE] [--artist ARTIST] [--limit N]
python3 cli.py list-books
python3 cli.py import-folder <path> [--dry-run]
python3 cli.py stats
python3 cli.py search <query>

# pdf_generator.py (CLI directe)
python3 backend/services/pdf_generator.py --book-id 1
python3 backend/services/pdf_generator.py --songs 1,2,3 --title "Mon Book" --instrument guitar
python3 backend/services/pdf_generator.py --songs 1,2,3 --no-cover --no-toc --no-index
python3 backend/services/pdf_generator.py --songs 1,2,3 --output-dir /tmp/books

# batch_import.py
python3 scripts/batch_import.py /chemin/vers/dossier [--dry-run]

# db_backup.py
python3 db_backup.py
```

### 6.4 Pages HTML

| Route | Template | Description |
|-------|----------|-------------|
| `/` et `/catalog` | `catalog.html` | Grille de morceaux avec recherche/filtres/modal edition |
| `/book-builder` | `book_builder.html` | Deux panneaux : catalogue filtrable + book (drag & drop) |
| `/import` | `import.html` | Page d'import PDF |
| `/settings` | `settings.html` | Page parametres |

Fichier source : `backend/app.py` (routes @app.route)

---

## 7. Exigences Non-Fonctionnelles

### 7.1 Performance

| Metrique | Cible | Implementation |
|----------|-------|----------------|
| Changement de book (GUI) | < 0.2s | Widget recycling + structures O(1) |
| Affichage catalogue (GUI) | Instantane | MAX_DISPLAY=50 + overflow label |
| Generation PDF 50 morceaux | < 10s | Thread background + PdfMerger |
| Recherche catalogue (Web) | < 300ms | Debounce 300ms + SQLite index |
| Temps reponse API | < 200ms | SQLite local, pas de reseau |

### 7.2 Securite

- **Authentification** : Aucune (application locale, single user)
- **Validation des entrees** : Verification cote serveur de la compatibilite instrument (`has_instrument()`)
- **Upload** : Extension limitee a `.pdf`, taille max 50 MB (`MAX_CONTENT_LENGTH`)
- **CORS** : Active via Flask-CORS (necessaire pour eventuel acces cross-origin)
- **Suppression fichiers** : La suppression d'un morceau ne supprime PAS le fichier PDF source (commentee dans le code)

### 7.3 Fiabilite

- **Backup automatique** : `db_backup.py`, rotation 10 derniers, execution manuelle ou programmable via cron
- **Gestion d'erreurs PDF** : Les morceaux sans fichier PDF sont ignores lors de la generation (pas d'arret)
- **Gestion d'erreurs GUI** : La generation en thread background capture les exceptions et les affiche dans un CTkTextbox copiable
- **Fichiers temporaires** : Nettoyes dans le bloc `finally` du generateur, meme en cas d'erreur
- **Recovery** : Restauration de la base via copie du backup : `cp data/backups/catalog_*.bak data/catalog.db`

### 7.4 Limites connues

- **Generation web non implementee** : L'endpoint `POST /api/books/<id>/generate` retourne 501. La generation fonctionne uniquement via GUI workflow ou CLI
- **Upload PDF non implemente** : L'endpoint `POST /api/import/pdf` retourne 501. L'import se fait via scripts ou GUI
- **Export catalogue non implemente** : L'endpoint `GET /api/export/catalog` retourne 501
- **Multi-versions non automatise** : La generation de 3 versions (guitare/basse/violon) depuis un seul workflow n'est pas implementee. Chaque version doit etre generee separement
- **Pas de preview PDF web** : Le preview web (`/api/books/<id>/preview`) retourne uniquement la TOC en JSON, pas un apercu visuel du PDF
- **Instruments fixes a 3** : guitar, bass, violin. Pas d'ajout dynamique d'instruments
- **Recherche texte simple** : Pas de recherche full-text, utilise ILIKE SQL (accent-insensitive non garanti)

---

## 8. Deploiement & Configuration

### 8.1 Prerequis

- Python 3.8+
- pip
- Aucune dependance systeme externe
- Pour la GUI : environnement graphique X11 (DISPLAY)

### 8.2 Installation

```bash
cd /data/projects/music-book
pip install -r requirements.txt
```

Les repertoires sont crees automatiquement au demarrage via `config.py ensure_directories()` :
- `data/imports/`
- `data/generated/`
- `data/exports/`
- `data/pdfs/guitar/`
- `data/pdfs/bass/`
- `data/pdfs/violin/`

### 8.3 Variables d'environnement

| Variable | Description | Requis | Defaut |
|----------|-------------|--------|--------|
| `SECRET_KEY` | Cle secrete Flask | Non | `dev-secret-key-change-in-production` |
| `DISPLAY` | Display X11 (GUI uniquement) | Non | `:1` (via script shell) |

Toute la configuration est centralisee dans `backend/config.py` (classe `Config`).

### 8.4 Lancement

```bash
# Interface Web (recommandee pour catalogage)
./start.sh
# → http://localhost:5051

# GUI Tkinter (legacy)
./lancer_music_book.sh

# GUI Workflow CustomTkinter (recommandee pour generation)
./lancer_workflow.sh

# CLI
python3 cli.py stats
python3 cli.py list-songs --genre "Rock"

# Generation directe
cd backend && python3 services/pdf_generator.py --book-id 1
```

### 8.5 Port reseau

- **Port** : 5051 (enregistre dans `/data/projects/infrastructure/data/port_registry.json`)
- **Bind** : 0.0.0.0 (accessible depuis le reseau local)
- **Debug** : `True` (auto-reload actif)

### 8.6 Configuration applicative

```python
# backend/config.py - Extraits de la classe Config

PORT = 5051
HOST = '0.0.0.0'
DEBUG = True

SQLALCHEMY_DATABASE_URI = f'sqlite:///{BASE_DIR}/data/catalog.db'
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

INSTRUMENTS = ['guitar', 'bass', 'violin']
INSTRUMENT_LABELS = {
    'guitar': 'Guitare',
    'bass': 'Basse',
    'violin': 'Violon'
}

DIFFICULTY_LEVELS = ['easy', 'medium', 'advanced']
DIFFICULTY_LABELS = {
    'easy': 'Facile',
    'medium': 'Moyen',
    'advanced': 'Avance'
}

PDF_STORAGE = {
    'guitar': '{BASE_DIR}/data/pdfs/guitar',
    'bass': '{BASE_DIR}/data/pdfs/bass',
    'violin': '{BASE_DIR}/data/pdfs/violin'
}
```

### 8.7 Frontend (CSS variables)

```css
/* frontend/static/css/style.css */
:root {
    --primary-color: #2563eb;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --danger-color: #ef4444;
    --warning-color: #f59e0b;
    --bg-color: #f8fafc;
    --card-bg: #ffffff;
    --text-color: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
}
```

---

## 9. Glossaire

| Terme | Definition |
|-------|-----------|
| Book | Un livre de partitions assemble a partir de morceaux selectionnes, avec configuration et PDF genere |
| Song | Un morceau de musique reference dans le catalogue, avec metadonnees et lien vers un fichier PDF source |
| TOC | Table des matieres (Table of Contents), generee automatiquement avec numeros de page |
| Index | Liste alphabetique en fin de book, organisee par titre, artiste ou genre |
| Overlay | Calque transparent superpose a chaque page PDF pour ajouter numeros de page et en-tetes |
| Widget Recycling | Pattern de performance GUI : pool de widgets pre-crees, reutilises avec nouveau contenu au lieu d'etre detruits/recrees |
| Source | Origine de la partition PDF (Ultimate Guitar, Songsterr, La Boite a chansons) |
| Type | Type de notation musicale : `chords` (accords) ou `tab` (tablature) |
| Instrument | Un des 3 instruments supportes : guitar, bass, violin |
| Batch Import | Import en masse de fichiers PDF avec detection automatique des metadonnees depuis le nom de fichier |
| Two-pass Generation | Technique de generation PDF en deux passes : la premiere calcule le nombre de pages systeme, la seconde regenere TOC et index avec la pagination exacte |
| System Pages | Pages generees par reportlab (couverture, TOC, index) par opposition aux pages de morceaux (PDF sources fusionnes) |

---

## Annexes

### A. Scripts utilitaires

| Script | Usage | Emplacement |
|--------|-------|-------------|
| `scripts/batch_import.py` | Import masse avec detection metadonnees | `python3 scripts/batch_import.py /chemin [--dry-run]` |
| `scripts/import_chords_folder.py` | Import avec regex compiles, mode clean | `python3 scripts/import_chords_folder.py` |
| `scripts/extract_metadata_from_pdf.py` | Extraction tonalite/difficulte depuis contenu PDF | `python3 scripts/extract_metadata_from_pdf.py <fichier.pdf>` |
| `scripts/generate_dummy_catalog.py` | Generation 31 morceaux de test | `python3 scripts/generate_dummy_catalog.py` |
| `db_backup.py` | Backup DB avec rotation | `python3 db_backup.py` |

### B. Patterns de detection des noms de fichiers

```
Ultimate Guitar :
  "Title Chords (ver N) by Artisttabs @ Ultimate Guitar Archive.pdf"
  "Title Chords by Artisttabs @ Ultimate Guitar Archive.pdf"
  "Title Tab (ver N) by Artisttabs @ Ultimate Guitar Archive.pdf"

Songsterr :
  "Title Tab by Artist _ Songsterr Tabs with Rhythm.pdf"
  "Title Bass Tab by Artist _ Songsterr Tabs with Rhythm_bass.pdf"

La Boite a chansons :
  "Title - Artist - La Boite a chansons.pdf"
```

### C. Historique des versions

| Version | Date | Changements |
|---------|------|-------------|
| 0.1.0 | 2025-12 | Creation initiale : catalogue, book builder web, generation PDF basique |
| 0.2.0 | 2025-12-23 | Fix sauvegarde books (ajout colonne pdf_path), amelioration erreurs |
| 0.3.0 | 2026-02-23 | GUI workflow CustomTkinter, widget recycling (perf x10), renommage books, index artiste/genre |
| 2.0 (spec) | 2026-03-13 | Reecriture complete de la specification technique |
