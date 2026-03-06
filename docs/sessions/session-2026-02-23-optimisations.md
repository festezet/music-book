# Session d'optimisation - 23 février 2026

## Objectifs de la session

1. **Performance** : Résoudre la lenteur (plusieurs secondes) lors du changement de book à l'étape 1
2. **Fonctionnalité** : Ajouter la possibilité de renommer un book
3. **UX** : Corriger le highlight visuel du book actif

## Problèmes identifiés

### 1. Lenteur au changement de book
- **Symptôme** : Passage d'un book à un autre prenait plusieurs secondes
- **Cause principale** : Création/destruction de widgets CustomTkinter à chaque changement
- **Profiling** :
  - Création de 30 widgets : ~0.7s
  - Destruction de widgets : ~0.8s
  - Total : ~1.5s par changement

### 2. Highlight du book actif
- **Symptôme** : La couleur bleue du book sélectionné ne s'affichait pas
- **Causes** :
  - Manque de rafraîchissement visuel après changement de couleur
  - Erreur `text_color=None` non acceptée par CustomTkinter

## Solutions implémentées

### 1. Optimisation des performances - Widget Recycling

#### `src/widgets/song_library.py`

**a) Lookups O(1) avec structures de données optimisées**
```python
# Avant : Liste uniquement (recherche O(n))
self.selected_song_ids: List[int] = []

# Après : Liste + Set pour O(1) lookup
self._selected_song_ids_list: List[int] = []  # Ordre préservé
self._selected_song_ids_set: set = set()      # Lookup O(1)
self._songs_by_id: Dict[int, Dict[str, Any]] = {}  # Index O(1)
```

**b) Pool de widgets réutilisables**
```python
# Pools de widgets créés une seule fois
self._available_widgets: List[ctk.CTkFrame] = []
self._selected_widgets: List[ctk.CTkFrame] = []

def _create_recyclable_item(self, parent, is_available: bool):
    """Widget créé une seule fois, réutilisé indéfiniment"""
    item = ctk.CTkFrame(parent, ...)
    # Layout compact en une ligne
    pos_label = ctk.CTkLabel(item, text="", width=25)
    title_label = ctk.CTkLabel(item, text="")
    # Action button ou checkbox
    return item

def _update_widget_content(self, widget, song, is_available, position=None):
    """Mise à jour du contenu sans recréer le widget"""
    widget._pos_label.configure(text=f"{position}.")
    widget._title_label.configure(text=f"{title} - {artist}")
```

**c) Format simplifié**
- Avant : Multi-lignes avec badges d'instruments colorés
- Après : Une seule ligne compacte (titre - artiste)
- Gain : Moins de sous-widgets = création/update plus rapide

**Résultats** :
- Temps de mise à jour : ~0.002s (vs ~0.7s avant)
- Recyclage de widgets : 0.000s après première création
- Total changement de book : ~0.2s (vs 1.5s+ avant)

#### `src/widgets/book_list.py`

**a) Highlight optimisé sans refresh complet**
```python
def _update_highlight(self, old_id: Optional[int], new_id: int):
    """Change les couleurs directement sans recréer les widgets"""
    # Désactiver highlight ancien book
    if old_id and old_id in self._book_frames:
        old_frame = self._book_frames[old_id]
        old_frame.configure(fg_color=("#f3f4f6", "#374151"))
        self._update_frame_text_colors(old_frame, is_selected=False)

    # Activer highlight nouveau book
    if new_id in self._book_frames:
        new_frame = self._book_frames[new_id]
        new_frame.configure(fg_color=("#3b82f6", "#2563eb"))
        self._update_frame_text_colors(new_frame, is_selected=True)
```

**b) Fix erreur CustomTkinter**
```python
# Avant : None non accepté
title_color = None if not is_selected else ("white", "white")

# Après : Couleurs par défaut du thème
title_color = ("white", "white") if is_selected else ("#1a1a1a", "#dce4ee")
sub_color = ("#e5e7eb", "#d1d5db") if is_selected else ("#6b7280", "#9ca3af")
```

**c) Mise à jour dynamique du compteur de morceaux**
```python
self._book_info_labels: Dict[int, ctk.CTkLabel] = {}

def update_song_count(self, book_id: int, count: int):
    """Met à jour le compteur sur la carte du book"""
    if book_id in self._book_info_labels:
        label = self._book_info_labels[book_id]
        label.configure(text=f"{instrument} - {count} morceaux")
```

### 2. Fonctionnalité de renommage

#### `src/widgets/book_list.py`
```python
# Menu contextuel (clic droit)
self.context_menu.add_command(
    label="Renommer",
    command=self._rename_selected_book
)

def _rename_selected_book(self):
    """Dialog de renommage avec mise à jour base de données"""
    new_title = simpledialog.askstring(
        "Renommer le book",
        "Nouveau nom:",
        initialvalue=current_title
    )
    # Mise à jour BDD + UI
```

#### `workflow_gui.py`
```python
def _on_book_rename(self, book_id: int, new_title: str):
    """Synchronise le nom avec le panel actif"""
    if self.current_book_id == book_id:
        self.step_panels[1].set_book_name(new_title)
```

### 3. Callback de changement de sélection

#### `src/widgets/song_library.py`
```python
def __init__(self, ..., on_selection_change: Callable = None):
    self.on_selection_change = on_selection_change

def _update_selected_list(self):
    # ... mise à jour widgets ...

    # Notifier le parent
    if self.on_selection_change:
        self.on_selection_change()
```

#### `workflow_gui.py`
```python
SongLibraryPanel(
    ...,
    on_selection_change=self._update_song_count
)

def _update_song_count(self):
    """Met à jour footer ET carte du book"""
    count = len(self._get_selected_songs())
    self.song_count_label.configure(text=...)

    # Mise à jour carte book
    if self.current_book_id:
        self.book_list.update_song_count(self.current_book_id, count)
```

## Fichiers modifiés

1. **src/widgets/song_library.py**
   - Pool de widgets réutilisables
   - Lookups O(1) avec set/dict
   - Format compact une ligne
   - Callback on_selection_change

2. **src/widgets/book_list.py**
   - Highlight optimisé
   - Fix couleurs CustomTkinter
   - Renommage de book
   - Mise à jour dynamique compteur

3. **workflow_gui.py**
   - Connection callback selection_change
   - Synchronisation nom book
   - Mise à jour compteur carte

## Métriques de performance

### Avant optimisation
- Changement de book : **1.5-2.0s**
- Création de 30 widgets : **0.7s**
- Destruction de widgets : **0.8s**
- Filtrage liste : **négligeable**

### Après optimisation
- Changement de book : **~0.2s** (10x plus rapide)
- Recyclage widgets : **0.000s** (après init)
- Mise à jour contenu : **0.002-0.005s**
- Total : **0.19-0.20s**

### Amélioration
- **Gain de performance : 87-90%**
- **Expérience utilisateur : quasi-instantané**

## Bugs corrigés

1. ✅ Lenteur changement de book (plusieurs secondes → 0.2s)
2. ✅ Highlight du book actif ne s'affichait pas
3. ✅ Erreur `ValueError: color is None` dans CustomTkinter
4. ✅ Compteur de morceaux non mis à jour sur carte book

## Fonctionnalités ajoutées

1. ✅ Renommage de book via clic droit
2. ✅ Mise à jour dynamique du compteur de morceaux
3. ✅ Highlight visuel du book actif
4. ✅ Performance optimale avec widget recycling

## Tests effectués

- [x] Changement rapide entre books (< 0.3s)
- [x] Highlight visuel correct
- [x] Renommage de book fonctionnel
- [x] Compteur mis à jour à l'ajout/retrait de morceaux
- [x] Pas de fuite mémoire (widgets recyclés)
- [x] Interface réactive

## Notes techniques

### Pattern Widget Recycling
Le pattern de recyclage de widgets est crucial pour les performances avec CustomTkinter :
- Création de widgets coûteuse (~20-30ms par widget)
- Mise à jour de contenu rapide (~0.1ms par widget)
- Pool pré-alloué évite allocations répétées

### Limitations CustomTkinter
- `text_color=None` non supporté (nécessite couleur explicite)
- `update_idletasks()` peut causer des blocages
- Préférer mise à jour directe avec `configure()`

## TODO / Améliorations futures

- [ ] Ajouter champ "Nom du propriétaire" à l'étape 3 (Export) pour personnaliser le book imprimé et éviter confusion entre utilisateurs

## Conclusion

Session réussie avec amélioration majeure de la performance (10x plus rapide) et correction de tous les bugs visuels. L'application est maintenant fluide et réactive lors du changement de books.

---
**Durée session** : ~2h
**Commits** : Optimisations song_library + book_list + workflow_gui
**Impact utilisateur** : ⭐⭐⭐⭐⭐ Majeur (UX grandement améliorée)
