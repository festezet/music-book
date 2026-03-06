# Structure du Projet Music Book Generator

## Vue d'ensemble

```
music-book/
├── backend/                    # Application Flask
│   ├── app.py                 # Point d'entrée Flask
│   ├── config.py              # Configuration (ports, chemins, etc.)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py          # Endpoints API REST
│   └── models/
│       ├── __init__.py
│       ├── song.py            # Modèle Song (morceaux)
│       ├── book.py            # Modèle Book (livres)
│       └── book_song.py       # Association Book ↔ Song
│
├── frontend/                   # Interface web
│   ├── templates/             # Pages HTML (Jinja2)
│   │   ├── base.html         # Template de base
│   │   ├── catalog.html      # Gestion du catalogue
│   │   ├── book_builder.html # Construction de books
│   │   ├── import.html       # Import de PDF
│   │   └── settings.html     # Paramètres
│   └── static/
│       ├── css/
│       │   └── style.css     # Styles CSS
│       └── js/
│           ├── app.js        # Utilitaires JavaScript
│           ├── catalog.js    # Logique catalogue
│           └── book_builder.js # Logique book builder
│
├── data/                       # Données et fichiers
│   ├── catalog.db             # Base SQLite (créée au 1er lancement)
│   ├── pdfs/                  # PDF sources par instrument
│   │   ├── guitar/
│   │   ├── bass/
│   │   └── violin/
│   ├── imports/               # Upload temporaire
│   ├── exports/               # Export CSV/JSON
│   └── generated/             # PDF books générés
│
├── scripts/                    # Scripts utilitaires
│   └── generate_dummy_catalog.py  # Génération données de test
│
├── docs/                       # Documentation
│   ├── SPECIFICATIONS.md      # Spécifications détaillées
│   └── STRUCTURE.md           # Ce fichier
│
├── .gitignore                  # Exclusions Git
├── README.md                   # Documentation principale
├── requirements.txt            # Dépendances Python
└── start.sh                    # Script de lancement
```

## Fichiers créés

### Backend (Python/Flask)

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `backend/app.py` | ~70 | Application Flask principale, routes HTML |
| `backend/config.py` | ~80 | Configuration (ports, chemins, constantes) |
| `backend/api/routes.py` | ~300 | Endpoints API REST (CRUD catalog, books) |
| `backend/models/song.py` | ~80 | Modèle SQLAlchemy pour les morceaux |
| `backend/models/book.py` | ~70 | Modèle SQLAlchemy pour les books |
| `backend/models/book_song.py` | ~35 | Association many-to-many Book ↔ Song |

### Frontend (HTML/CSS/JS)

| Fichier | Lignes | Description |
|---------|--------|-------------|
| `frontend/templates/base.html` | ~40 | Template de base avec navbar |
| `frontend/templates/catalog.html` | ~100 | Page de gestion du catalogue |
| `frontend/templates/book_builder.html` | ~90 | Page de construction de books |
| `frontend/templates/import.html` | ~70 | Page d'import de PDF |
| `frontend/templates/settings.html` | ~80 | Page de paramètres |
| `frontend/static/css/style.css` | ~450 | Styles CSS complets |
| `frontend/static/js/app.js` | ~60 | Utilitaires JavaScript |
| `frontend/static/js/catalog.js` | ~200 | Logique page catalogue |
| `frontend/static/js/book_builder.js` | ~250 | Logique page book builder |

### Documentation

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation utilisateur |
| `docs/SPECIFICATIONS.md` | Spécifications techniques complètes |
| `docs/STRUCTURE.md` | Structure du projet (ce fichier) |

### Configuration

| Fichier | Description |
|---------|-------------|
| `requirements.txt` | Dépendances Python (Flask, SQLAlchemy, PDF libs) |
| `.gitignore` | Exclusions Git (DB, venv, cache, etc.) |
| `start.sh` | Script de lancement de l'application |

### Scripts

| Fichier | Description |
|---------|-------------|
| `scripts/generate_dummy_catalog.py` | Génération de 30 morceaux de test |

## Base de données SQLite

### Table `songs`
Stocke les morceaux du catalogue :
- Métadonnées : titre, artiste, tonalité, tempo, genre
- Difficulté : easy/medium/advanced
- Instruments : JSON array (guitar, bass, violin)
- Fichier PDF : chemin vers le PDF source

### Table `books`
Stocke les livres créés :
- Configuration : titre, instrument cible
- Options : page de garde, TOC, index
- Format : A4/Letter, portrait/paysage

### Table `book_songs`
Association many-to-many entre `books` et `songs` :
- Position : ordre des morceaux dans le book

## Fonctionnalités implémentées

### ✅ Phase 1 : Structure et catalogue (FAIT)
- [x] Structure complète du projet
- [x] Modèles de base de données (SQLAlchemy)
- [x] API REST complète (CRUD catalog, books)
- [x] Interface catalogue (ajout, édition, filtres)
- [x] Interface book builder (drag & drop)
- [x] Génération de données de test

### ⏳ Phase 2 : Fonctionnalités à implémenter

#### Import de PDF
- [ ] Upload de fichiers PDF
- [ ] Extraction métadonnées (PyPDF2)
- [ ] Génération de miniatures (pdf2image)
- [ ] Stockage organisé par instrument

#### Génération de PDF
- [ ] Service de génération (reportlab)
- [ ] Page de garde personnalisée
- [ ] Table des matières automatique
- [ ] Index alphabétique
- [ ] Numérotation des pages
- [ ] Fusion des PDF sources (PyPDF2)
- [ ] Bookmarks PDF (navigation)
- [ ] Génération des 3 versions (Guitar, Bass, Violin)

#### Export/Import
- [ ] Export catalogue (CSV, JSON)
- [ ] Import métadonnées en masse
- [ ] Scan de dossier local

## Stack Technique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Python + Flask | 3.8+ |
| Base de données | SQLite | - |
| ORM | SQLAlchemy | 2.0.23 |
| PDF manipulation | PyPDF2 + reportlab | - |
| Frontend | HTML5 + CSS3 + Vanilla JS | - |
| Serveur | Flask dev server | Port 5051 |

## Prochaines étapes

### Priorité 1 : Import de PDF
1. Implémenter l'upload dans `api/routes.py`
2. Créer `services/pdf_parser.py` pour extraction métadonnées
3. Tester avec quelques PDF réels

### Priorité 2 : Génération de PDF
1. Créer `services/pdf_generator.py`
2. Implémenter génération page de garde (reportlab)
3. Implémenter table des matières
4. Fusion des PDF sources (PyPDF2)
5. Tester génération d'un book complet

### Priorité 3 : Polish
1. Améliorer l'UI (notifications, loading states)
2. Ajouter validation des données
3. Gérer les erreurs côté client
4. Optimiser les performances

## Lancement rapide

```bash
# Installation
cd /data/projects/music-book
pip install -r requirements.txt

# Génération de données de test
python3 scripts/generate_dummy_catalog.py

# Lancement
./start.sh

# Ouvrir dans le navigateur
# http://localhost:5051/catalog
```

---

*Dernière mise à jour : 2025-12-01*
*Projet créé avec Claude Code*
