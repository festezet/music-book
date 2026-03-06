# Index de la documentation - Music Book Generator

Guide de navigation dans la documentation du projet.

---

## 📖 Documentation principale

### Pour démarrer
- **[README.md](../README.md)** - Vue d'ensemble, installation, utilisation
- **[ROADMAP.md](../ROADMAP.md)** - Feuille de route et vision du projet
- **[CHANGELOG.md](../CHANGELOG.md)** - Historique des versions et changements

### Documentation technique
- **[SPECIFICATIONS.md](SPECIFICATIONS.md)** - Spécifications techniques détaillées
- **[STRUCTURE.md](STRUCTURE.md)** - Architecture du projet
- **[GUI_GUIDE.md](GUI_GUIDE.md)** - Guide de l'interface graphique

---

## 📚 Sessions de développement

Documentation détaillée des sessions de travail avec analyses techniques.

### Session 2026-02-23 - Optimisations Performance
**Fichier** : [session-2026-02-23-optimisations.md](sessions/session-2026-02-23-optimisations.md)

**Sujets** :
- Widget Recycling Pattern
- Optimisation performance (10x plus rapide)
- Lookups O(1) avec structures optimisées
- Renommage de books
- Mise à jour dynamique des compteurs
- Fix highlight visuel

**Métriques** :
- Changement book : 1.5s → 0.2s (90% amélioration)
- Création widgets : 0.7s → 0.000s (recyclage)

**Fichiers modifiés** :
- `src/widgets/song_library.py`
- `src/widgets/book_list.py`
- `workflow_gui.py`

---

## 🔍 Navigation par sujet

### Performance
- [session-2026-02-23-optimisations.md](sessions/session-2026-02-23-optimisations.md) - Widget recycling et optimisations

### Interface utilisateur
- [GUI_GUIDE.md](GUI_GUIDE.md) - Guide interface graphique
- [session-2026-02-23-optimisations.md](sessions/session-2026-02-23-optimisations.md#2-fonctionnalité-de-renommage) - Renommage de books

### Architecture
- [STRUCTURE.md](STRUCTURE.md) - Structure du projet
- [SPECIFICATIONS.md](SPECIFICATIONS.md) - Spécifications techniques

### Historique
- [CHANGELOG.md](../CHANGELOG.md) - Toutes les versions
- [sessions/](sessions/) - Sessions de développement

---

## 📋 Par type de document

### Guides utilisateur
1. [README.md](../README.md) - Installation et utilisation
2. [GUI_GUIDE.md](GUI_GUIDE.md) - Interface graphique

### Guides développeur
1. [SPECIFICATIONS.md](SPECIFICATIONS.md) - Spécifications techniques
2. [STRUCTURE.md](STRUCTURE.md) - Architecture
3. [sessions/](sessions/) - Documentation technique des sessions

### Planification
1. [ROADMAP.md](../ROADMAP.md) - Feuille de route
2. [CHANGELOG.md](../CHANGELOG.md) - Historique

---

## 🗂️ Structure des dossiers

```
docs/
├── INDEX.md                    # Ce fichier - Index de navigation
├── SPECIFICATIONS.md           # Spécifications techniques
├── STRUCTURE.md               # Architecture du projet
├── GUI_GUIDE.md               # Guide interface graphique
└── sessions/                  # Documentation des sessions
    └── session-2026-02-23-optimisations.md

racine/
├── README.md                  # Vue d'ensemble
├── ROADMAP.md                # Feuille de route
├── CHANGELOG.md              # Historique des versions
└── SESSION_SUMMARY.md        # Résumé dernière session
```

---

## 🔗 Liens rapides

### Démarrage rapide
- [Installation](../README.md#installation)
- [Lancement](../README.md#lancement)
- [Utilisation](../README.md#utilisation)

### Développement
- [Structure du projet](STRUCTURE.md)
- [Stack technique](../README.md#stack-technique)
- [API Endpoints](../README.md#api-endpoints)

### Historique
- [Version actuelle (0.3.0)](../CHANGELOG.md#030---2026-02-23)
- [Dernière session](sessions/session-2026-02-23-optimisations.md)
- [Roadmap v0.4.0](../ROADMAP.md#v040-personnalisation-avancée)

---

## 📝 Conventions

### Nommage des fichiers de session
Format : `session-YYYY-MM-DD-theme.md`

Exemple : `session-2026-02-23-optimisations.md`

### Structure d'une session
1. Objectifs
2. Problèmes identifiés
3. Solutions implémentées
4. Fichiers modifiés
5. Métriques
6. Tests
7. Conclusion

---

## 🆕 Dernière mise à jour

**Date** : 2026-02-23
**Version** : 0.3.0
**Dernière session** : [Optimisations Performance](sessions/session-2026-02-23-optimisations.md)

---

**Navigation** : [Racine](../README.md) | [Roadmap](../ROADMAP.md) | [Changelog](../CHANGELOG.md)
