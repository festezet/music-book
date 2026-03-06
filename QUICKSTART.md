# Music Book Generator - Guide de Démarrage Rapide

## 🎯 Objectif
Créer des livres de partitions/chords/lyrics structurés à partir de fichiers PDF, avec génération automatique de 3 versions (Guitare, Basse, Violon).

## 📦 Installation

### 1. Installer les dépendances
```bash
cd /data/projects/music-book
pip install -r requirements.txt
```

### 2. Générer le catalogue de test
```bash
python3 scripts/generate_dummy_catalog.py
```

Cela créera **30 morceaux de test** répartis entre :
- Guitare (20 morceaux)
- Basse (10 morceaux)
- Violon (7 morceaux)
- Multi-instruments (certains morceaux)

### 3. Lancer l'application

**Interface GUI (Recommandé)** :
```bash
./lancer_music_book.sh
# Ou : ~/lancer_music_book.sh
```

**Interface Web (Alternative)** :
```bash
./start.sh
# Puis ouvrir : http://localhost:5051/catalog
```

## 🚀 Utilisation

### Interface GUI (Tkinter)

L'application dispose de **3 onglets** :

#### 📚 Onglet 1 : Catalogue
- **Visualiser** : Liste de tous les morceaux avec filtres (recherche, instrument, difficulté)
- **Ajouter** : Bouton "➕ Ajouter un morceau" → formulaire complet
- **Éditer** : Double-clic sur un morceau ou bouton "✏️ Éditer"
- **Supprimer** : Sélectionner + bouton "🗑️ Supprimer"

#### 📖 Onglet 2 : Book Builder
- **Configuration** : Titre, instrument cible, options (page de garde, TOC, index)
- **Panneau gauche** : Morceaux disponibles
- **Panneau droit** : Morceaux du book
- **Actions** :
  - Sélectionner morceaux → "➡️ Ajouter au book"
  - Réorganiser : boutons "⬆️ Monter" / "⬇️ Descendre"
  - Retirer : bouton "🗑️ Retirer"
- **Sauvegarder** : "💾 Sauvegarder Book" (stocke en BDD)
- **Générer** : "📄 Générer PDF (3 versions)" (Phase 3 - à implémenter)

#### 📥 Onglet 3 : Import PDF
- Bouton "📁 Sélectionner des fichiers PDF"
- Sélection multiple de fichiers
- Formulaire métadonnées pour chaque fichier
- Ajout automatique au catalogue

### Interface Web (Alternative)

#### Étape 1 : Gérer le catalogue
1. Ouvrir **Catalogue** (http://localhost:5051/catalog)
2. Parcourir les morceaux générés
3. Cliquer sur un morceau pour éditer les métadonnées
4. Utiliser les filtres (instrument, difficulté, recherche)
5. Ajouter de nouveaux morceaux avec le bouton **Ajouter un morceau**

#### Étape 2 : Créer un Music Book
1. Ouvrir **Book Builder** (http://localhost:5051/book-builder)
2. Cliquer sur **Nouveau Book**
3. Renseigner :
   - Titre (ex: "Music Book - Guitare")
   - Instrument cible (Guitare, Basse, ou Violon)
   - Options (page de garde, table des matières, index)
4. Glisser-déposer des morceaux depuis le panneau gauche vers le book
5. Réorganiser l'ordre si nécessaire

#### Étape 3 : Générer les PDF (à implémenter)
1. Cliquer sur **Générer PDF**
2. Les 3 versions seront créées :
   - `Music_Book_Guitar_2025-12-01.pdf`
   - `Music_Book_Bass_2025-12-01.pdf`
   - `Music_Book_Violin_2025-12-01.pdf`
3. Télécharger depuis `/data/projects/music-book/data/generated/`

## 📁 Structure des Données

### Catalogue (SQLite)
```
/data/projects/music-book/data/catalog.db
```

### PDF sources (à ajouter manuellement pour l'instant)
```
/data/projects/music-book/data/pdfs/
├── guitar/    # PDF pour guitare
├── bass/      # PDF pour basse
└── violin/    # PDF pour violon
```

### PDF générés (après génération)
```
/data/projects/music-book/data/generated/
```

## 🎨 Fonctionnalités Actuelles

### ✅ Implémenté
- Catalogue de morceaux avec CRUD complet
- Métadonnées complètes (titre, artiste, tonalité, difficulté, instruments)
- Filtres et recherche
- Création de books
- Sélection de morceaux (drag & drop)
- Preview du book (nombre de pages estimé)
- Interface responsive

### ⏳ À implémenter
- Upload de PDF réels
- Extraction automatique des métadonnées
- Génération des PDF (page de garde, TOC, index, fusion)
- Export/Import de catalogue

## 🔧 Configuration

### Modifier le port
Éditer `backend/config.py` :
```python
PORT = 5051  # Changer ici
```

### Modifier les chemins de stockage
Éditer `backend/config.py` :
```python
PDF_STORAGE = {
    'guitar': '/chemin/personnalisé/guitar',
    'bass': '/chemin/personnalisé/bass',
    'violin': '/chemin/personnalisé/violin'
}
```

## 📚 Exemple de Workflow

### Scenario : Créer un book de 10 morceaux de guitare faciles

1. **Filtrer le catalogue**
   - Ouvrir Catalogue
   - Filtre instrument : Guitare
   - Filtre difficulté : Facile
   - → 5 morceaux disponibles

2. **Créer le book**
   - Book Builder → Nouveau Book
   - Titre : "Débutant Guitare"
   - Instrument : Guitare

3. **Ajouter les morceaux**
   - Glisser-déposer les 5 morceaux
   - Réorganiser dans l'ordre souhaité

4. **Générer**
   - Cliquer sur Générer PDF
   - Télécharger le fichier généré

## 🐛 Dépannage

### Le serveur ne démarre pas
```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Vérifier que le port 5051 est libre
netstat -tuln | grep 5051
```

### La base de données est vide
```bash
# Régénérer le catalogue de test
python3 scripts/generate_dummy_catalog.py
```

### Erreur "Module not found"
```bash
# S'assurer d'être dans le bon répertoire
cd /data/projects/music-book/backend
python3 app.py
```

## 📖 Documentation Complète

- **README.md** : Vue d'ensemble du projet
- **docs/SPECIFICATIONS.md** : Spécifications techniques détaillées
- **docs/STRUCTURE.md** : Structure du projet et architecture

## 🎯 Prochaines Étapes de Développement

### Phase 2 : Import de PDF
1. Implémenter l'upload de fichiers PDF
2. Extraire les métadonnées automatiquement
3. Générer des miniatures (preview)

### Phase 3 : Génération de PDF
1. Créer le service de génération
2. Implémenter page de garde, TOC, index
3. Fusionner les PDF sources
4. Générer les 3 versions (Guitar, Bass, Violin)

### Phase 4 : Polish
1. Améliorer l'interface utilisateur
2. Ajouter des notifications/toasts
3. Gérer les erreurs côté client
4. Optimiser les performances

---

**Projet créé le : 2025-12-01**
**Stack : Python 3 + Flask + SQLite + Vanilla JS**
**Port : 5051**

*Bon développement musical !* 🎸🎵
