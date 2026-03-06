# Music Book Generator

Application web de création de livres de partitions/chords/lyrics structurés à partir de fichiers PDF.

## 🎯 Objectif

Générer automatiquement des **Music Books** organisés avec :
- Table des matières interactive
- Numérotation automatique des pages
- Index alphabétique
- **3 versions déclinées** : Guitare, Basse, Violon

## Fonctionnalités principales

### 1. Catalogue de morceaux
- Upload de PDF (partitions, chords, lyrics)
- Métadonnées complètes (titre, artiste, tonalité, difficulté, instruments)
- Filtres et recherche avancée
- Preview des PDF

### 2. Construction de books
- Sélection des morceaux (drag & drop)
- Réorganisation de l'ordre
- Configuration (page de garde, table des matières, index)
- Preview avant génération

### 3. Génération multi-versions
- **1 workflow → 3 PDF** (Guitare, Basse, Violon)
- Filtrage automatique par instrument
- PDF structuré avec bookmarks
- Export prêt à imprimer

## 📂 Structure

```
music-book/
├── backend/              # Flask + logique métier
│   ├── app.py
│   ├── models/          # SQLAlchemy (Song, Book)
│   ├── services/        # PDF parser, generator, catalog
│   └── api/             # REST endpoints
├── frontend/
│   ├── templates/       # Jinja2 (catalog, book builder)
│   └── static/          # CSS + JS
├── data/
│   ├── catalog.db       # Base SQLite
│   ├── pdfs/            # PDF sources (guitar, bass, violin)
│   ├── imports/         # Upload temporaire
│   └── generated/       # PDF books générés
├── scripts/
│   ├── generate_dummy_catalog.py
│   └── import_folder.py
└── docs/
    └── SPECIFICATIONS.md
```

## Stack technique

- **Backend** : Python 3 + Flask
- **PDF** : PyPDF2/pypdf + reportlab
- **Base de données** : SQLite
- **Frontend** : HTML5/CSS3 + JavaScript vanilla

## 🚀 Installation

### Prérequis
- Python 3.8+
- pip

### Installation des dépendances

```bash
cd /data/projects/music-book
pip install -r requirements.txt
```

## Lancement

### Interface GUI (Recommandé)

```bash
# Lancement direct
./lancer_music_book.sh

# Ou depuis le home
~/lancer_music_book.sh
```

### Interface Web (Alternative)

```bash
./start.sh
```

Puis ouvrir : **http://localhost:5051**

## Utilisation

### 1. Construire le catalogue
1. Aller dans **Catalogue**
2. Uploader des PDF (partitions, chords, lyrics)
3. Renseigner les métadonnées :
   - Titre, artiste, tonalité
   - Instruments compatibles (Guitare, Basse, Violon)
   - Difficulté, genre, tags

### 2. Créer un Music Book
1. Aller dans **Book Builder**
2. Créer un nouveau book (titre + instrument cible)
3. Sélectionner les morceaux depuis le catalogue
4. Réorganiser l'ordre (drag & drop)
5. Configurer les options (table des matières, index, page de garde)

### 3. Générer les PDF
1. Cliquer sur **Générer les 3 versions**
2. Télécharger les PDF générés :
   - `Music_Book_Guitar_2025-12-01.pdf`
   - `Music_Book_Bass_2025-12-01.pdf`
   - `Music_Book_Violin_2025-12-01.pdf`

## Exemples d'utilisation

### Import en masse depuis un dossier
```bash
python3 scripts/import_folder.py /chemin/vers/dossier/pdf
```

### Génération de données de test
```bash
python3 scripts/generate_dummy_catalog.py
```

## Workflow typique

```
1. Upload PDF → 2. Métadonnées → 3. Catalogue
                                      ↓
4. Sélection morceaux ← 5. Filtres (instrument, difficulté)
        ↓
6. Construction book → 7. Réorganisation → 8. Preview
                                               ↓
                                    9. Génération 3 versions
                                               ↓
                                    10. Téléchargement PDF
```

## API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/catalog` | Liste des morceaux |
| `POST` | `/api/catalog` | Ajouter un morceau |
| `GET` | `/api/books` | Liste des books |
| `POST` | `/api/books` | Créer un book |
| `POST` | `/api/books/<id>/generate` | Générer les PDF |
| `POST` | `/api/import/pdf` | Upload PDF |
| `GET` | `/api/export/catalog` | Export catalogue |

## Configuration

### Port par défaut
- **5051** (configurable dans `backend/config.py`)

### Stockage
- PDF sources : `/data/pdfs/{guitar,bass,violin}/`
- PDF générés : `/data/generated/`
- Base de données : `/data/catalog.db`

## Problemes Connus

### ~~Enregistrement des Books~~ (RÉSOLU 2025-12-23)
**Symptome** : Les books générés n'étaient pas sauvegardés en base de données.

**Cause** : La colonne `pdf_path` n'existait pas dans la table `books`, mais le code tentait de l'utiliser. L'erreur était capturée silencieusement.

**Solution appliquée** :
- Ajout de la colonne `pdf_path` au modèle `Book` et à la BDD
- Amélioration du traitement d'erreur avec affichage dans l'UI
- Ajout de la date dans la liste des books pour différencier les entrées

## 🎉 Nouveautés v0.3.0 (Février 2026)

### Performance x10 🚀
- **Changement de book quasi-instantané** : 0.2s vs 2s+ auparavant
- **Widget Recycling** : Pool de widgets réutilisables pour zéro latence
- **Lookups optimisés** : Structures O(1) pour recherches ultra-rapides

### Nouvelles fonctionnalités ✨
- **Renommage de books** : Clic droit → "Renommer"
- **Mise à jour dynamique** : Compteur de morceaux en temps réel sur les cartes
- **Highlight visuel** : Book actif clairement identifié en bleu

### Détails techniques
Voir [Session d'optimisation du 23 février 2026](docs/sessions/session-2026-02-23-optimisations.md) pour l'analyse complète.

## Roadmap

Voir [ROADMAP.md](ROADMAP.md) pour la feuille de route détaillée.

### Version 0.3.0 (actuelle) ✅
- [x] Catalogue de morceaux
- [x] Métadonnées complètes
- [x] Construction de books
- [x] Génération multi-versions (3 PDF)
- [x] Table des matières + index
- [x] Gestionnaire de bibliothèque (import multiple, édition)
- [x] **Performance optimisée (10x plus rapide)** 🚀
- [x] **Renommage de books** ✨
- [x] **Interface fluide et réactive** 💨

### Version 0.4.0 (prochaine) 📋
- [ ] Nom du propriétaire sur couverture
- [ ] Prévisualisation PDF avant génération
- [ ] Templates de couverture personnalisables
- [ ] Export multi-formats (ePub, HTML)

### Version 1.0 (objectif Décembre 2026) 🎯
- [ ] Tests automatisés complets
- [ ] Documentation utilisateur exhaustive
- [ ] Support multi-langues
- [ ] Installateur autonome
- [ ] 10 000+ téléchargements

## Documentation

- [SPECIFICATIONS.md](docs/SPECIFICATIONS.md) - Détails techniques complets
- [ROADMAP.md](ROADMAP.md) - Feuille de route et jalons
- [CHANGELOG.md](CHANGELOG.md) - Historique des versions
- [Sessions](docs/sessions/) - Documentation des sessions de développement

## Licence

Projet personnel - Tous droits réservés

---

**Version actuelle** : 0.3.0
**Dernière mise à jour** : 2026-02-23
