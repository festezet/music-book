# PROJECT_STATUS — Music Book Generator (PRJ-015)
Derniere MAJ : 2026-03-27

## Etat courant
- Application web de creation de livres de partitions/chords/lyrics — version 0.4.1
- **Workflow 4 etapes + Dark Theme** (v0.4.0)
  - Book Builder : sidebar books + workflow 4 steps + dark theme
  - 6 modules JS : orchestrateur + sidebar + step1-4
  - Modele Book etendu : 11 colonnes (index, page_numbers, margins, filename_pattern, footer_text)
- **PDF enrichi** (v0.4.1)
  - Liens cliquables sur TOC + 3 index (annotations /Link, architecture `_pdf_link_data` + `file_offsets`)
  - 3 index convertis en canvas pour coordonnees precises
  - Bookmarks PDF (outline sidebar) pour chaque morceau
  - Pieds de page : texte configurable a gauche ("Music Book" par defaut) + numero x/total a droite
  - En-tetes morceaux : titre/artiste en bleu clair
- Stack : Flask + PyPDF2 + reportlab + SQLite + SQLAlchemy

## Fichiers cles
- `backend/services/pdf_generator.py` — BookConfig + MusicBookGenerator (orchestrateur 4 phases)
- `backend/services/pdf_section_generators.py` — Cover, TOC, 3 index (canvas + link_data)
- `backend/services/pdf_overlay.py` — Merge, footers, _add_internal_links, bookmarks
- `backend/models/book.py` — Book model (11 colonnes etendues + footer_text)
- `backend/api/routes.py` — REST endpoints + /catalog/filters
- `frontend/templates/book_builder.html` — Layout sidebar + 4 step panels

## Prochaines etapes
- v0.5.0 : nom proprietaire sur couverture, previsualisation PDF, templates couverture
- v1.0 (objectif dec 2026) : tests automatises, doc utilisateur, multi-langues

## Problemes connus
- 3 morceaux sans PDF dans le catalogue → liens target hors limites (filtres par bounds check, pas d'erreur)
