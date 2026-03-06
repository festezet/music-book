# Music Book Generator - Guide Interface GUI

**Date création** : 2025-12-01
**Type** : Application Tkinter (desktop)
**Fichier** : `music_book_gui.py`

---

## 🎯 Vue d'ensemble

Interface graphique desktop (Tkinter) pour Music Book Generator.

**Avantages GUI vs Web** :
- ✅ Pas besoin de navigateur
- ✅ Application native standalone
- ✅ Sélection de fichiers intégrée
- ✅ Plus rapide et réactif
- ✅ Fonctionne hors ligne

---

## 🚀 Lancement

```bash
# Depuis le projet
cd /data/projects/music-book
./lancer_music_book.sh

# Depuis n'importe où
~/lancer_music_book.sh
```

---

## 📱 Interface - 3 Onglets

### 📚 Onglet 1 : Catalogue

**Objectif** : Gérer la bibliothèque de morceaux

#### Filtres (haut de page)
- **Recherche** : Filtre en temps réel (titre, artiste)
- **Instrument** : Guitare / Basse / Violon
- **Difficulté** : Facile / Moyen / Avancé

#### Actions disponibles
| Bouton | Action |
|--------|--------|
| ➕ Ajouter un morceau | Ouvre formulaire vide |
| ✏️ Éditer | Éditer morceau sélectionné |
| 🗑️ Supprimer | Supprimer après confirmation |
| 🔄 Actualiser | Recharger la liste |

#### Liste des morceaux (Treeview)
Colonnes :
- **Titre** : Nom du morceau
- **Artiste** : Nom de l'artiste
- **Instruments** : Guitare, Basse, Violon
- **Difficulté** : Facile, Moyen, Avancé
- **Tonalité** : C, Dm, G7, etc.
- **Pages** : Nombre de pages

**Interaction** :
- Double-clic sur une ligne → Édition
- Sélection simple

#### Formulaire Ajout/Édition
Champs :
- **Titre*** (obligatoire)
- **Artiste**
- **Tonalité** (ex: C, Dm, G7)
- **Tempo (BPM)** (nombre entier)
- **Genre** (Rock, Jazz, Blues, etc.)
- **Difficulté** (liste déroulante)
- **Instruments** (checkboxes : Guitare, Basse, Violon)
- **Nombre de pages** (nombre entier)
- **Notes** (zone de texte libre)

Boutons :
- 💾 Enregistrer
- ❌ Annuler

---

### 📖 Onglet 2 : Book Builder

**Objectif** : Construire des livres de partitions

#### Section 1 : Configuration du Book
| Champ | Description |
|-------|-------------|
| **Titre** | Nom du book (ex: "Music Book - Guitare") |
| **Instrument** | Guitare / Basse / Violon (cible) |
| **Page de garde** | Checkbox |
| **Table des matières** | Checkbox |
| **Index alphabétique** | Checkbox |

Boutons :
- 💾 Sauvegarder Book → Stocke en base de données
- 📄 Générer PDF (3 versions) → Phase 3 (à implémenter)

#### Section 2 : Panneaux Gauche/Droite

**Panneau Gauche** : Morceaux disponibles
- Liste de tous les morceaux du catalogue
- Colonnes : Titre, Artiste
- Sélection multiple (Ctrl+Clic, Shift+Clic)

**Panneau Droit** : Morceaux du book
- Morceaux ajoutés au book en cours
- Colonnes : Titre, Artiste, Pages
- Ordre = ordre dans le book final

#### Actions
| Bouton | Action |
|--------|--------|
| ➡️ Ajouter au book | Ajoute sélection gauche → droite |
| ⬆️ Monter | Déplace morceau sélectionné vers le haut |
| ⬇️ Descendre | Déplace morceau sélectionné vers le bas |
| 🗑️ Retirer | Retire morceau du book |

#### Info Book (bas du panneau droit)
- Nombre de morceaux
- Estimation pages totales (morceaux + pages système)

---

### 📥 Onglet 3 : Import PDF

**Objectif** : Importer des fichiers PDF dans le catalogue

#### Workflow
1. Cliquer sur **📁 Sélectionner des fichiers PDF**
2. Naviguer dans l'explorateur de fichiers
3. Sélectionner un ou plusieurs PDF (multi-sélection possible)
4. Pour chaque fichier :
   - Formulaire s'ouvre automatiquement
   - Titre pré-rempli (nom du fichier sans extension)
   - Renseigner métadonnées
   - Enregistrer
5. Fichiers ajoutés au catalogue

**Formats acceptés** : PDF uniquement
**Taille max** : 50 MB par fichier

---

## 🗄️ Base de Données SQLite

**Localisation** : `/data/projects/music-book/data/catalog.db`

### Persistance automatique
- Créée au premier lancement
- Tous les morceaux et books sont sauvegardés
- Survit aux redémarrages de l'application
- Aucune configuration requise

### Tables
1. **songs** : Morceaux du catalogue
2. **books** : Books créés
3. **book_songs** : Association Book ↔ Song avec position

---

## 💡 Workflow Typique

### Workflow 1 : Ajouter des morceaux manuellement

1. Lancer GUI : `~/lancer_music_book.sh`
2. Onglet **Catalogue**
3. Cliquer **➕ Ajouter un morceau**
4. Remplir formulaire (titre, artiste, instruments, etc.)
5. **💾 Enregistrer**
6. Répéter pour chaque morceau

### Workflow 2 : Importer des PDF

1. Lancer GUI
2. Onglet **Import PDF**
3. **📁 Sélectionner des fichiers PDF**
4. Choisir plusieurs PDF
5. Pour chaque PDF :
   - Vérifier/compléter métadonnées
   - **💾 Enregistrer**
6. Retourner à l'onglet **Catalogue** pour voir les morceaux

### Workflow 3 : Créer un Music Book

1. Onglet **Book Builder**
2. Configurer :
   - Titre : "Music Book - Guitare"
   - Instrument : Guitare
   - Options : Cocher page de garde, TOC, index
3. **Panneau gauche** : Sélectionner morceaux (Ctrl+Clic pour multi-sélection)
4. Cliquer **➡️ Ajouter au book**
5. **Panneau droit** : Réorganiser avec ⬆️ / ⬇️ si besoin
6. **💾 Sauvegarder Book** (stocke en BDD)
7. **📄 Générer PDF (3 versions)** (Phase 3 - à implémenter)

---

## 🔧 Fonctionnalités Implémentées

### ✅ Opérationnel
- Catalogue complet (CRUD : Create, Read, Update, Delete)
- Filtres en temps réel (recherche, instrument, difficulté)
- Formulaires de saisie complets
- Book Builder avec sélection multi-morceaux
- Réorganisation de l'ordre des morceaux (monter/descendre)
- Import de PDF avec sélection de fichiers
- Sauvegarde automatique en base SQLite
- Calcul estimation pages du book

### ⏳ À implémenter (Phase 3)
- Génération des 3 PDF (Guitar, Bass, Violin)
- Page de garde (reportlab)
- Table des matières automatique
- Index alphabétique
- Numérotation des pages
- Fusion des PDF sources
- Bookmarks PDF (navigation)

---

## 🎨 Style et Ergonomie

### Thème
- Thème Tkinter : `clam`
- Couleurs sobres et professionnelles
- Boutons avec emojis pour faciliter la navigation

### Dimensions
- Fenêtre principale : 1200x800 pixels
- Formulaires : 500x600 pixels
- Responsive : Panneaux redimensionnables (PanedWindow)

### Raccourcis
- **Double-clic** sur morceau → Édition
- **Sélection multiple** : Ctrl+Clic, Shift+Clic

---

## 📊 Statistiques

**Fichier** : `music_book_gui.py`
**Lignes de code** : ~650 lignes
**Classes** :
- `MusicBookGUI` : Application principale
- `SongDialog` : Dialogue formulaire morceau

**Méthodes principales** :
- Catalogue : `refresh_catalog()`, `add_song()`, `edit_song()`, `delete_song()`
- Book Builder : `add_to_book()`, `remove_from_book()`, `move_up()`, `move_down()`, `save_book()`, `generate_books()`
- Import : `import_pdfs()`

---

## 🐛 Dépannage

### L'application ne démarre pas

```bash
# Vérifier Python 3
python3 --version

# Vérifier Tkinter
python3 -c "import tkinter"

# Installer si manquant
sudo apt install python3-tk

# Vérifier Flask
python3 -c "import flask"

# Installer dépendances
cd /data/projects/music-book
pip install -r requirements.txt
```

### Erreur "Base de données verrouillée"

La base SQLite ne supporte qu'une connexion en écriture à la fois.

Solution :
- Fermer l'application web (si lancée)
- Fermer les autres instances de la GUI
- Relancer

### Les filtres ne fonctionnent pas

- Actualiser avec le bouton 🔄
- Vérifier que les morceaux ont bien les métadonnées (instrument, difficulté)

---

## 📚 Documentation Complémentaire

- **README.md** : Vue d'ensemble du projet
- **QUICKSTART.md** : Guide de démarrage rapide
- **docs/SPECIFICATIONS.md** : Spécifications techniques complètes
- **PROJECT_STATUS.md** : Roadmap et état d'avancement

---

**Interface GUI créée le : 2025-12-01**
**Stack : Python 3 + Tkinter + SQLAlchemy + SQLite**
**Fichier principal : `music_book_gui.py`**
**Lanceur : `~/lancer_music_book.sh`**

*Bon usage !* 🎸🎵
