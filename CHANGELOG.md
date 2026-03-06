# Changelog - Music Book Generator

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [Unreleased]

### À venir
- Champ "Nom du propriétaire" à l'étape 3 (Export) pour personnaliser le book imprimé

---

## [0.3.0] - 2026-02-23

### ✨ Jalon : Performance & UX - Interface fluide

**Objectif atteint** : Changement de book quasi-instantané (<0.3s vs 2s+)

### Ajouté
- **Widget Recycling Pattern** : Pool de widgets réutilisables pour performances optimales
- **Renommage de book** : Clic droit → "Renommer" sur les cartes de books
- **Mise à jour dynamique** : Compteur de morceaux sur carte book mis à jour en temps réel
- **Callback selection_change** : Notification automatique des changements de sélection
- Documentation session détaillée : `docs/sessions/session-2026-02-23-optimisations.md`

### Amélioré
- **Performance x10** : Changement de book passe de 1.5-2.0s à 0.19-0.20s
- **Lookups O(1)** : Structures optimisées (set + dict) pour recherches rapides
- **Format compact** : Widgets simplifiés en une ligne (titre - artiste)
- **Highlight visuel** : Mise à jour directe sans refresh complet de la liste

### Corrigé
- ❌ → ✅ Lenteur critique au changement de book (plusieurs secondes)
- ❌ → ✅ Highlight du book actif ne s'affichait pas
- ❌ → ✅ Erreur `ValueError: color is None` avec CustomTkinter
- ❌ → ✅ Compteur de morceaux non synchronisé sur carte book

### Détails techniques
- **Recyclage de widgets** : Création unique, mise à jour répétée
- **Optimisation mémoire** : Pas de fuites, widgets réutilisés
- **Structure de données** : Double indexation (list + set) pour O(1) + ordre

### Fichiers modifiés
- `src/widgets/song_library.py` - Widget recycling + lookups O(1)
- `src/widgets/book_list.py` - Highlight optimisé + renommage + compteur
- `workflow_gui.py` - Callbacks synchronisation

### Métriques
| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| Changement book | 1.5-2.0s | 0.19-0.20s | **90%** |
| Création widgets | 0.7s | 0.000s (recyclés) | **100%** |
| Mise à jour UI | N/A | 0.002-0.005s | Nouveau |

---

## [0.2.0] - Précédent

### Fonctionnalités principales
- Interface workflow en 4 étapes
- Sélection et tri des morceaux
- Configuration du book (TOC, index, pages)
- Options d'export PDF
- Génération de books avec suivi de progression
- Gestion de bibliothèque de morceaux

### Technologies
- CustomTkinter pour l'interface graphique
- SQLAlchemy pour la base de données
- ReportLab pour génération PDF
- Flask pour l'architecture backend

---

## [0.1.0] - Initial

### Première version
- Architecture de base du projet
- Modèles de données (Song, Book, BookSong)
- Interface CLI basique
- Génération PDF simple

---

## Légende des symboles

- ✨ Nouvelle fonctionnalité majeure
- 🚀 Amélioration de performance
- 🐛 Correction de bug
- 📝 Documentation
- 🔧 Configuration / Outillage
- 💄 Style / Interface
- ♻️ Refactorisation
- ⚡ Performance
- 🔥 Suppression de code

---

## Jalons à venir

### [0.4.0] - Personnalisation avancée
- [ ] Nom du propriétaire sur la couverture
- [ ] Choix de thèmes visuels
- [ ] Export multi-formats (PDF, ePub)

### [0.5.0] - Collaboration
- [ ] Partage de books entre utilisateurs
- [ ] Import/Export de bibliothèques
- [ ] Synchronisation cloud

### [1.0.0] - Version stable
- [ ] Tests complets
- [ ] Documentation utilisateur complète
- [ ] Installateur autonome
- [ ] Support multi-langues
