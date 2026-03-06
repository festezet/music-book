# Session 2026-01-03 - Music Book PDF Pagination Fix

**Date** : 2026-01-03
**Duree** : ~90 minutes
**Projet** : PRJ-015 music-book

## Contexte

L'application music-book generait des PDF avec des numeros de page incorrects dans la table des matieres et les index. Les morceaux multi-pages n'etaient pas pris en compte correctement.

De plus, l'application crashait (segfault) apres un clic, lie a l'utilisation d'emojis/Unicode dans les widgets CustomTkinter.

## Problemes Resolus

### 1. Crash Segfault CustomTkinter (CRITIQUE)

**Cause** : Utilisation d'emojis et caracteres Unicode speciaux dans les widgets CTk
- Emojis : `✓`, `✅`, `❌`, `⚠️`, `📁`
- Caracteres accentues dans certains contextes

**Solution** :
- Remplacement des emojis par du texte ASCII : `[x]`, `[OK]`, `[ERR]`, `WARN:`
- Remplacement de `Étape` par `Etape`
- Ajout de blocs try/except avec traceback dans les fonctions critiques

**Fichiers modifies** :
- `src/widgets/song_library.py` - try/except dans `_create_song_item`, `_update_available_list`, `_update_selected_list`
- `src/widgets/generation.py` - Remplacement emojis
- `src/widgets/export_options.py` - Remplacement emoji dossier
- `workflow_gui.py` - Remplacement `Étape` par `Etape`

### 2. Pagination PDF Incorrecte

**Cause** : Le calcul des pages de depart (`start_page`) utilisait `song.pages` de la BDD au lieu de compter les pages reelles des PDF sources.

**Solution** : Refactoring complet de `pdf_generator.py` en 3 phases :

1. **Phase 1** : Generer les pages systeme (cover, TOC, index) et compter leurs pages reelles avec `_count_pdf_pages()`

2. **Phase 2** : Calculer les vraies pages de depart en comptant les pages reelles de chaque PDF source :
```python
if song.pdf_path and os.path.exists(song.pdf_path):
    actual_pages = self._count_pdf_pages(song.pdf_path)
    song.pages = actual_pages
```

3. **Phase 3** : Regenerer TOC et Index avec les bons numeros de page

**Nouvelles methodes** :
- `_count_pdf_pages(pdf_path)` : Compte les pages d'un PDF avec PyPDF2
- `_estimate_start_pages(songs, config)` : Estimation pour premiere passe

### 3. Headers sur Pages Multi-pages

**Cause** : Le mapping `song_page_map` dans `_add_footers` utilisait aussi `song.pages` de la BDD.

**Solution** : Compter les pages reelles dans `_add_footers` egalement :
```python
if song.pdf_path and os.path.exists(song.pdf_path):
    song_pages = self._count_pdf_pages(song.pdf_path)
```

Le header affiche maintenant : `Titre - Artiste (1/3)`, `(2/3)`, `(3/3)` sur chaque page du morceau.

### 4. TOC avec Numeros en Bleu

Les numeros de page dans la TOC sont affiches en bleu (`#2563eb`) pour une meilleure lisibilite.

Note : Les liens cliquables ont ete tentes mais ReportLab ne supporte pas les liens vers des anchors non encore definis. Implementation future possible avec PyPDF2 post-fusion.

## Fichiers Modifies

| Fichier | Modifications |
|---------|---------------|
| `backend/services/pdf_generator.py` | Refactoring pagination 3 phases, `_count_pdf_pages()`, `_estimate_start_pages()` |
| `src/widgets/song_library.py` | Try/except, badges inline, suppression `_update_badges()` call |
| `src/widgets/generation.py` | Remplacement emojis par ASCII |
| `src/widgets/export_options.py` | Remplacement emoji dossier |
| `workflow_gui.py` | Remplacement `Étape` par `Etape` |

## Validation

- [x] Application demarre sans crash
- [x] Clic sur book ne cause plus de segfault
- [x] TOC affiche les bons numeros de page
- [x] Morceaux multi-pages ont la bonne page de depart
- [x] Headers affichent le titre sur toutes les pages du morceau
- [x] Numeros de page en bleu dans la TOC

## Lecons Apprises

**CRITIQUE - CustomTkinter + Emojis = SEGFAULT**

Ne JAMAIS utiliser d'emojis ou caracteres Unicode speciaux dans les widgets CustomTkinter (CTkButton, CTkLabel, etc.). Cause un crash systeme immediat (segmentation fault, exit code 139) sans exception Python.

A ajouter dans `.claude/LESSONS_LEARNED.md` si pas deja present.
