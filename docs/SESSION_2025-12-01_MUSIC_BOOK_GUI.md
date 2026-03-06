# Session 2025-12-01 : Music Book Generator - Interface GUI

## Contexte

Suite à la création du projet Music Book Generator (Phase 1 web terminée), développement de l'**interface GUI Tkinter** pour une expérience desktop native.

---

## Objectif

Créer une interface graphique desktop (Tkinter) pour remplacer/compléter l'interface web, avec :
- Gestion complète du catalogue (CRUD)
- Construction de books (sélection multi-morceaux, réorganisation)
- Import de PDF avec sélection de fichiers
- Persistance via base SQLite (partagée avec interface web)

---

## Réalisations

### 1. Application GUI Complète

**Fichier** : `music_book_gui.py` (~650 lignes)

#### Architecture
- **Classe MusicBookGUI** : Application principale
- **Classe SongDialog** : Dialogue formulaire (ajout/édition morceau)
- **3 onglets** : Catalogue, Book Builder, Import PDF

#### Technologies
- **GUI** : Tkinter (bibliothèque standard Python)
- **Thème** : `clam` (sobre et professionnel)
- **Base de données** : SQLAlchemy + SQLite (partagée avec web)
- **Widgets** : Treeview, Notebook, PanedWindow, Checkbuttons

### 2. Fonctionnalités Implémentées

#### 📚 Onglet Catalogue
- **Filtres en temps réel** :
  - Recherche (titre, artiste)
  - Instrument (guitare, basse, violon)
  - Difficulté (facile, moyen, avancé)
- **Actions** :
  - ➕ Ajouter un morceau (formulaire complet)
  - ✏️ Éditer (double-clic ou bouton)
  - 🗑️ Supprimer (avec confirmation)
  - 🔄 Actualiser
- **Liste Treeview** : 6 colonnes (titre, artiste, instruments, difficulté, tonalité, pages)

#### 📖 Onglet Book Builder
- **Configuration du book** :
  - Titre (ex: "Music Book - Guitare")
  - Instrument cible (guitare/basse/violon)
  - Options : Page de garde, TOC, Index (checkboxes)
- **Panneaux gauche/droite** :
  - Gauche : Morceaux disponibles
  - Droite : Morceaux du book (ordre)
- **Actions** :
  - ➡️ Ajouter au book (multi-sélection supportée)
  - ⬆️ Monter / ⬇️ Descendre (réorganiser)
  - 🗑️ Retirer
  - 💾 Sauvegarder book (stocke en BDD)
  - 📄 Générer PDF (Phase 3 - placeholder)
- **Info temps réel** : Nombre morceaux, estimation pages

#### 📥 Onglet Import PDF
- Bouton sélection fichiers (explorateur système)
- Multi-sélection de PDF
- Formulaire métadonnées par fichier
- Ajout automatique au catalogue

### 3. Formulaire Song (Dialogue)

**Champs** :
- Titre* (obligatoire)
- Artiste
- Tonalité (C, Dm, G7, etc.)
- Tempo (BPM)
- Genre
- Difficulté (liste déroulante)
- Instruments (checkboxes : guitare, basse, violon)
- Nombre de pages
- Notes (zone texte)

**Validation** :
- Vérification titre non vide
- Conversion types (tempo, pages → int)
- Collecte instruments sélectionnés

### 4. Scripts et Lanceurs

#### `lancer_music_book.sh`
Script de lancement avec vérifications :
- Vérification Python 3
- Vérification Tkinter (`python3-tk`)
- Vérification Flask (dépendances backend)
- Messages d'erreur clairs si manquant

#### Lien symbolique
```bash
~/lancer_music_book.sh → /data/projects/music-book/lancer_music_book.sh
```

Permet lancement depuis n'importe où : `~/lancer_music_book.sh`

### 5. Documentation Créée

| Fichier | Description |
|---------|-------------|
| `docs/GUI_GUIDE.md` | Guide complet interface GUI (~300 lignes) |
| Mise à jour `README.md` | Section lancement GUI |
| Mise à jour `QUICKSTART.md` | Instructions GUI détaillées |

---

## Architecture Technique

### Base de Données SQLite

**Fichier** : `/data/projects/music-book/data/catalog.db`

**Persistance** :
- Créée automatiquement au premier lancement
- Partagée entre interface web et GUI
- Tous les morceaux et books sauvegardés
- Survit aux redémarrages

### Tables
1. **songs** : Morceaux du catalogue
2. **books** : Books créés
3. **book_songs** : Association Book ↔ Song (avec position)

### Intégration Backend Flask

La GUI utilise le backend Flask existant :
- Import des modèles SQLAlchemy (Song, Book, BookSong)
- Utilisation du contexte Flask (`with app.app_context()`)
- Réutilisation complète de la logique métier
- Pas de duplication de code

---

## Workflow Utilisateur

### Workflow 1 : Importer des PDF

```
1. Lancer ~/lancer_music_book.sh
2. Onglet "Import PDF"
3. Cliquer "📁 Sélectionner des fichiers PDF"
4. Choisir plusieurs PDF
5. Pour chaque PDF :
   - Vérifier/compléter métadonnées
   - Enregistrer
6. Fichiers ajoutés au catalogue
```

### Workflow 2 : Créer un Music Book

```
1. Onglet "Book Builder"
2. Configuration :
   - Titre : "Music Book - Guitare"
   - Instrument : Guitare
   - Cocher : Page de garde, TOC, Index
3. Panneau gauche : Sélectionner morceaux (Ctrl+Clic)
4. Cliquer "➡️ Ajouter au book"
5. Panneau droit : Réorganiser (⬆️ / ⬇️)
6. "💾 Sauvegarder Book"
7. "📄 Générer PDF" (Phase 3)
```

---

## Statistiques

### Code
- **Fichier GUI** : `music_book_gui.py` (~650 lignes)
- **Classes** : 2 (MusicBookGUI, SongDialog)
- **Méthodes** : ~20
- **Widgets Tkinter** : Notebook, Treeview, Entry, Combobox, Checkbutton, Text, Button, PanedWindow

### Projet Total (Phase 1 + GUI)
- **Fichiers créés** : 26 (24 Phase 1 + 2 GUI)
- **Lignes de code** : ~2200
- **Documentation** : 6 fichiers

---

## Avantages GUI vs Web

| Critère | GUI Tkinter | Web Flask |
|---------|-------------|-----------|
| Installation | Tkinter inclus Python | Navigateur requis |
| Sélection fichiers | Native OS | Upload web limité |
| Réactivité | Instantanée | Requêtes HTTP |
| Offline | ✅ Oui | ❌ Serveur requis |
| Multi-fenêtres | ✅ Oui | ❌ Onglets navigateur |
| Expérience | Desktop native | Application web |

**Choix recommandé** : **GUI Tkinter** pour usage personnel

---

## Fonctionnalités Implémentées vs À Faire

### ✅ Phase 1 (TERMINÉE)
- Structure complète backend/frontend
- API REST (13 endpoints)
- Interface web (4 pages)
- **Interface GUI (3 onglets)** ⭐ NOUVEAU
- Base de données SQLite
- Script génération données test

### ⏳ Phase 2 (À FAIRE - 2-3h)
- Upload de PDF réels (stockage organisé)
- Extraction métadonnées (PyPDF2)
- Génération miniatures (pdf2image)

### ⏳ Phase 3 (À FAIRE - 4-5h)
- Service `pdf_generator.py`
- Page de garde (reportlab)
- Table des matières automatique
- Fusion PDF sources (PyPDF2)
- Numérotation des pages
- Index alphabétique
- Bookmarks PDF
- **Génération 3 versions** (Guitar, Bass, Violin)

---

## Commandes Rapides

```bash
# Lancement GUI
~/lancer_music_book.sh

# Lancement web (alternative)
cd /data/projects/music-book
./start.sh
# Puis : http://localhost:5051

# Générer données de test
python3 scripts/generate_dummy_catalog.py

# Localisation BDD
/data/projects/music-book/data/catalog.db
```

---

## Prochaines Étapes

### Phase 2 : Import PDF Réel
1. Implémenter stockage PDF organisé (`data/pdfs/{guitar,bass,violin}/`)
2. Extraction métadonnées basiques (nombre de pages via PyPDF2)
3. Génération miniatures (première page via pdf2image)
4. Tester avec quelques PDF réels

### Phase 3 : Génération PDF
1. Créer `services/pdf_generator.py`
2. Page de garde (reportlab avec titre, instrument, date)
3. Table des matières (liste morceaux + pages)
4. Fusion PDF sources (PyPDF2)
5. Numérotation pages
6. Index alphabétique
7. Tester génération complète d'un book

---

## Résumé

### Ce qui a été créé
- **Interface GUI Tkinter complète** (650 lignes)
- **3 onglets** : Catalogue, Book Builder, Import PDF
- **Persistance SQLite** : Base de données partagée web/GUI
- **Script de lancement** : `~/lancer_music_book.sh`
- **Documentation GUI** : `docs/GUI_GUIDE.md`

### Temps de développement
- Développement GUI : ~1h30
- Documentation : ~30 min
- **Total** : ~2h

### État du projet
- **Phase 1** : ✅ TERMINÉE (web + GUI)
- **Phase 2** : ⏳ Import PDF (2-3h)
- **Phase 3** : ⏳ Génération PDF (4-5h)

---

**Session terminée le : 2025-12-01**
**Interface GUI opérationnelle et testable**
**Prêt pour Phase 2 (Import PDF réels)**

*Projet créé avec Claude Code (compte Fabrice)*
