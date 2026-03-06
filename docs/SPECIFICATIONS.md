# Music Book Generator - Spécifications

## 1. Vue d'ensemble

### 1.1 Objectif
Application web de création de livres de partitions/chords/lyrics structurés à partir de fichiers PDF, avec génération automatique de :
- Table des matières
- Numérotation des pages
- Index alphabétique des morceaux
- 3 versions déclinées : Guitare, Basse, Violon

### 1.2 Stack Technique
- **Backend** : Python 3 + Flask
- **Manipulation PDF** : PyPDF2 / pypdf + reportlab (génération)
- **Base de données** : SQLite (catalogue des morceaux)
- **Frontend** : HTML5/Jinja2 + CSS3 + JavaScript vanilla
- **Export** : PDF structuré (avec bookmarks/table des matières)

### 1.3 Pourquoi cette approche ?
- Simple et autonome (pas de cloud, tout en local)
- Manipulation directe des PDF (pas de conversion)
- Portable (base SQLite pour le catalogue)
- Multi-versions (un workflow unique, 3 outputs)

## 2. Fonctionnalités Détaillées

### 2.1 Gestion du Catalogue

#### 2.1.1 Import de PDF
- Upload de fichiers PDF individuels (partitions, chords, lyrics)
- Extraction automatique des métadonnées :
  - Titre du morceau (via parsing du nom de fichier ou OCR optionnel)
  - Artiste
  - Nombre de pages
  - Tonalité
  - Difficulté (facile, moyen, avancé)
  - Instruments (guitare, basse, violon, tous)

#### 2.1.2 Métadonnées par morceau
| Champ | Type | Description |
|-------|------|-------------|
| Titre | String | Nom du morceau |
| Artiste | String | Nom de l'artiste/groupe |
| Tonalité | String | C, Dm, G7, etc. |
| Tempo | Integer | BPM (optionnel) |
| Genre | String | Rock, Jazz, Blues, etc. |
| Difficulté | Enum | Facile, Moyen, Avancé |
| Instruments | Multi-select | Guitare, Basse, Violon |
| Tags | String | Tags libres (acoustique, électrique, fingerstyle, etc.) |
| Fichier PDF | Path | Chemin vers le PDF source |
| Pages | Integer | Nombre de pages du PDF |
| Notes | Text | Commentaires libres |

#### 2.1.3 Organisation du catalogue
- Vue en grille avec miniatures des PDF
- Filtres :
  - Par instrument (Guitare, Basse, Violon)
  - Par difficulté
  - Par artiste
  - Par tonalité
  - Recherche texte libre
- Tri :
  - Alphabétique (titre)
  - Par artiste
  - Par date d'ajout
  - Par difficulté

### 2.2 Construction du Music Book

#### 2.2.1 Sélection des morceaux
- Interface drag & drop pour ordonner les morceaux
- Preview du PDF de chaque morceau
- Ajout/suppression de morceaux
- Réorganisation de l'ordre

#### 2.2.2 Configuration du Book
| Paramètre | Options | Défaut |
|-----------|---------|--------|
| Instrument | Guitare / Basse / Violon | Guitare |
| Titre du livre | Texte libre | "Music Book - [Instrument]" |
| Format de page | A4 / Letter | A4 |
| Orientation | Portrait / Paysage | Portrait |
| Numérotation | Bas de page / Haut de page | Bas de page |
| Table des matières | Oui / Non | Oui |
| Index alphabétique | Oui / Non | Oui |
| Page de garde | Oui / Non | Oui |

#### 2.2.3 Structure du PDF généré
```
Music Book - Guitare
├── Page de garde
│   ├── Titre du livre
│   ├── Instrument
│   ├── Date de génération
│   └── Nombre de morceaux
├── Table des matières (1-2 pages)
│   └── Liste des morceaux avec numéro de page
├── Morceaux (pages numérotées)
│   ├── Morceau 1 (pages X-Y)
│   ├── Morceau 2 (pages Z-W)
│   └── ...
└── Index alphabétique (1 page)
    └── Liste alphabétique avec numéro de page
```

### 2.3 Génération Multi-Versions

#### 2.3.1 Workflow de génération
1. **Sélection du projet** : Choisir les morceaux à inclure
2. **Génération des 3 versions** en parallèle :
   - `Music_Book_Guitar_2025-12-01.pdf`
   - `Music_Book_Bass_2025-12-01.pdf`
   - `Music_Book_Violin_2025-12-01.pdf`
3. **Filtrage automatique** : Seuls les morceaux compatibles avec l'instrument sont inclus
4. **Export** : Fichiers PDF dans `/data/generated/`

#### 2.3.2 Gestion des morceaux multi-instruments
- Si un morceau a les tags `[Guitare, Basse]` :
  - Il apparaît dans le book Guitare
  - Il apparaît dans le book Basse
  - Il n'apparaît PAS dans le book Violon

### 2.4 Visualisation et Preview

#### 2.4.1 Aperçu du catalogue
- Miniatures des PDF (première page)
- Métadonnées en survol
- Clic pour voir le PDF complet (inline viewer)

#### 2.4.2 Preview du book avant génération
- Aperçu de la table des matières
- Liste ordonnée des morceaux
- Nombre total de pages estimé
- Vérification des morceaux manquants pour un instrument

### 2.5 Import/Export

#### 2.5.1 Import
- Upload PDF par glisser-déposer (multi-fichiers)
- Import CSV de métadonnées (pour mise à jour en masse)
- Scan de dossier local (indexation automatique)

#### 2.5.2 Export
- PDF structuré (avec bookmarks PDF natifs)
- Export du catalogue (CSV, JSON)
- Export des métadonnées (backup)

## 3. Architecture Technique

### 3.1 Structure du projet
```
music-book/
├── backend/
│   ├── app.py                    # Application Flask principale
│   ├── config.py                 # Configuration
│   ├── api/
│   │   └── routes.py             # Endpoints API REST
│   ├── models/
│   │   ├── song.py               # Modèle Song (métadonnées)
│   │   ├── book.py               # Modèle Book (configuration)
│   │   └── book_song.py          # Association Book ↔ Song
│   └── services/
│       ├── pdf_parser.py         # Extraction métadonnées PDF
│       ├── pdf_generator.py      # Génération du book PDF
│       ├── catalog.py            # Gestion du catalogue
│       └── export.py             # Export multi-formats
├── frontend/
│   ├── templates/
│   │   ├── base.html
│   │   ├── catalog.html          # Gestion du catalogue
│   │   ├── book_builder.html     # Construction du book
│   │   ├── preview.html          # Preview avant génération
│   │   ├── settings.html         # Configuration
│   │   └── import.html           # Import de PDF
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           ├── app.js
│           ├── catalog.js        # Gestion catalogue
│           └── book_builder.js   # Drag & drop, réorganisation
├── data/
│   ├── catalog.db                # Base SQLite
│   ├── pdfs/
│   │   ├── guitar/               # PDF filtrés guitare
│   │   ├── bass/                 # PDF filtrés basse
│   │   └── violin/               # PDF filtrés violon
│   ├── imports/                  # PDF uploadés temporairement
│   ├── exports/                  # Export CSV/JSON
│   └── generated/                # PDF books générés
├── scripts/
│   ├── import_folder.py          # Import en masse depuis dossier
│   └── generate_dummy_catalog.py # Génération catalogue de test
├── docs/
│   └── SPECIFICATIONS.md
├── requirements.txt
├── start.sh
└── README.md
```

### 3.2 Base de données (SQLite)

#### 3.2.1 Table `songs`
```sql
CREATE TABLE songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255),
    key VARCHAR(10),          -- Tonalité (C, Dm, etc.)
    tempo INTEGER,            -- BPM
    genre VARCHAR(100),
    difficulty VARCHAR(20),   -- 'easy', 'medium', 'advanced'
    instruments TEXT,         -- JSON array: ["guitar", "bass"]
    tags TEXT,                -- JSON array: ["acoustic", "fingerstyle"]
    pdf_path VARCHAR(500) NOT NULL,
    pages INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.2.2 Table `books`
```sql
CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(255) NOT NULL,
    instrument VARCHAR(50) NOT NULL,  -- 'guitar', 'bass', 'violin'
    format VARCHAR(20) DEFAULT 'A4',
    orientation VARCHAR(20) DEFAULT 'portrait',
    include_toc BOOLEAN DEFAULT 1,
    include_index BOOLEAN DEFAULT 1,
    include_cover BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.2.3 Table `book_songs` (association)
```sql
CREATE TABLE book_songs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER NOT NULL,
    song_id INTEGER NOT NULL,
    position INTEGER NOT NULL,  -- Ordre dans le book
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (song_id) REFERENCES songs(id)
);
```

### 3.3 API Endpoints

```
GET  /api/catalog                 # Liste des morceaux (avec filtres)
GET  /api/catalog/<id>            # Détails d'un morceau
POST /api/catalog                 # Ajouter un morceau
PUT  /api/catalog/<id>            # Modifier métadonnées
DELETE /api/catalog/<id>          # Supprimer un morceau

GET  /api/books                   # Liste des books créés
POST /api/books                   # Créer un book
GET  /api/books/<id>              # Détails d'un book
PUT  /api/books/<id>              # Modifier un book
DELETE /api/books/<id>            # Supprimer un book

POST /api/books/<id>/add_song     # Ajouter un morceau au book
POST /api/books/<id>/reorder      # Réorganiser les morceaux
POST /api/books/<id>/generate     # Générer les PDF (3 versions)

POST /api/import/pdf              # Upload PDF
POST /api/import/folder           # Scanner un dossier
POST /api/import/metadata         # Import CSV métadonnées

GET  /api/export/catalog          # Export catalogue (JSON/CSV)
GET  /api/books/<id>/preview      # Preview du book (table des matières)
```

## 4. Workflow Utilisateur

### 4.1 Phase 1 : Construction du catalogue
1. Uploader des PDF (partitions, chords, lyrics)
2. Renseigner les métadonnées (titre, artiste, instrument, difficulté, etc.)
3. Taguer les morceaux (instruments compatibles)
4. Organiser par dossiers virtuels (optionnel)

### 4.2 Phase 2 : Construction du book
1. Créer un nouveau book (titre, instrument cible)
2. Filtrer le catalogue (par instrument, difficulté, artiste)
3. Sélectionner les morceaux à inclure
4. Réorganiser l'ordre (drag & drop)
5. Configurer les options (table des matières, index, page de garde)

### 4.3 Phase 3 : Génération
1. Preview de la structure (nombre de pages, table des matières)
2. Lancer la génération des 3 versions (Guitare, Basse, Violon)
3. Télécharger les PDF générés
4. Sauvegarder la configuration du book (pour regénération future)

## 5. Fonctionnalités avancées (futur)

### 5.1 Génération intelligente
- **Transposition automatique** : Adapter la tonalité d'un morceau
- **OCR des partitions** : Extraction automatique des métadonnées (titre, tonalité)
- **Détection d'instrument** : Analyse du contenu pour identifier l'instrument

### 5.2 Collaboration
- Export/import de books entre utilisateurs
- Partage de catalogue (format standardisé)

### 5.3 Print-ready
- Marges pour reliure
- Mode recto-verso (pages blanches insérées)
- Génération de PDF pour impression professionnelle

## 6. Contraintes techniques

### 6.1 Manipulation PDF
- **PyPDF2** ou **pypdf** : Fusion de PDF, extraction de pages
- **reportlab** : Génération de page de garde, table des matières, numérotation
- **pdfrw** : Manipulation des bookmarks PDF (table des matières interactive)

### 6.2 Performance
- Génération asynchrone (éviter de bloquer l'interface)
- Cache des miniatures (première page des PDF)
- Pagination du catalogue (si > 100 morceaux)

### 6.3 Stockage
- PDF stockés dans `/data/pdfs/{instrument}/`
- PDF générés dans `/data/generated/`
- Base SQLite : `/data/catalog.db`

## 7. Données de test

### 7.1 Catalogue de démonstration
Un script génère un catalogue de test avec :
- 50 morceaux factices
- Répartition : 30 guitare, 20 basse, 15 violon (certains multi-instruments)
- Métadonnées variées (artistes, tonalités, difficultés)
- PDF générés automatiquement (pages blanches avec titre)

```bash
python3 scripts/generate_dummy_catalog.py
```

## 8. Lancement

```bash
cd /data/projects/music-book
./start.sh
# Ouvrir http://localhost:5051
```

---

*Document créé le : 2025-12-01*
*Dernière mise à jour : 2025-12-01*
*Version : 1.0*
