/**
 * Book Builder - Step 1 : Selection des morceaux
 * Filtres, bibliotheque, selection, drag & drop, reorder
 */
(function() {

const BB = window.BookBuilder;

const step1 = {
    init() {
        this.bindEvents();
    },

    onEnter() {
        this.populateFilterDropdowns();
        this.loadAvailableSongs();
        this.renderSelected();
        this.updateBookNameDisplay();
        this.updateNextButton();
    },

    onLeave() {
        // Persist song order to backend
    },

    bindEvents() {
        // Search
        const searchInput = document.getElementById('step1Search');
        if (searchInput) {
            searchInput.addEventListener('input', BB.debounce(() => this.loadAvailableSongs(), 300));
        }

        // Filter dropdowns
        ['step1Sort', 'step1Instrument', 'step1Source', 'step1Genre', 'step1Artist'].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.addEventListener('change', () => this.loadAvailableSongs());
        });

        // Book name inline edit
        const nameEl = document.getElementById('step1BookName');
        if (nameEl) {
            nameEl.addEventListener('blur', () => this.saveBookName());
            nameEl.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') { e.preventDefault(); nameEl.blur(); }
            });
        }

        // Buttons
        document.getElementById('btnAddAll')?.addEventListener('click', () => this.addAllVisible());
        document.getElementById('btnMoveUp')?.addEventListener('click', () => this.moveSelected(-1));
        document.getElementById('btnMoveDown')?.addEventListener('click', () => this.moveSelected(1));
        document.getElementById('btnRemoveSelected')?.addEventListener('click', () => this.removeChecked());
        document.getElementById('btnClearAll')?.addEventListener('click', () => this.clearAll());
        document.getElementById('btnStep1Next')?.addEventListener('click', () => BB.nextStep());
    },

    updateBookNameDisplay() {
        const nameEl = document.getElementById('step1BookName');
        if (nameEl && BB.state.currentBook) {
            nameEl.textContent = BB.state.currentBook.title;
        }
    },

    async saveBookName() {
        const nameEl = document.getElementById('step1BookName');
        if (!nameEl || !BB.state.currentBook) return;
        const newTitle = nameEl.textContent.trim();
        if (newTitle && newTitle !== BB.state.currentBook.title) {
            await BB.saveBookSettings({ title: newTitle });
            BB.state.allBooks = await BB.api('/books');
            BB.modules.sidebar?.renderBookList();
        }
    },

    populateFilterDropdowns() {
        const f = BB.state.catalogFilters;

        this._populateSelect('step1Source', f.sources);
        this._populateSelect('step1Genre', f.genres);
        this._populateSelect('step1Artist', f.artists);
    },

    _populateSelect(id, values) {
        const sel = document.getElementById(id);
        if (!sel) return;
        const current = sel.value;
        // Keep first option (Tous)
        while (sel.options.length > 1) sel.remove(1);
        values.forEach(v => {
            const opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            sel.appendChild(opt);
        });
        sel.value = current || '';
    },

    async loadAvailableSongs() {
        const params = new URLSearchParams();
        const search = document.getElementById('step1Search')?.value;
        const sort = document.getElementById('step1Sort')?.value;
        const instrument = document.getElementById('step1Instrument')?.value;
        const source = document.getElementById('step1Source')?.value;
        const genre = document.getElementById('step1Genre')?.value;
        const artist = document.getElementById('step1Artist')?.value;

        if (search) params.append('search', search);
        if (sort) params.append('sort', sort);
        if (instrument) params.append('instrument', instrument);
        if (source) params.append('source', source);
        if (genre) params.append('genre', genre);
        if (artist) params.append('artist', artist);

        const endpoint = params.toString() ? `/catalog?${params}` : '/catalog';

        try {
            BB.state.availableSongs = await BB.api(endpoint);
            this.renderLibrary();
        } catch (error) {
            BB.notify('Erreur chargement catalogue', 'error');
        }
    },

    renderLibrary() {
        const list = document.getElementById('songLibraryList');
        if (!list) return;

        // Filter out songs already in book
        const bookSongIds = new Set(BB.state.bookSongs.map(s => s.id));
        const available = BB.state.availableSongs.filter(s => !bookSongIds.has(s.id));

        if (available.length === 0) {
            list.innerHTML = '<p class="empty-state" style="padding: 1rem;">Aucun morceau disponible</p>';
            return;
        }

        list.innerHTML = available.map(song => `
            <div class="song-library-item" data-id="${song.id}" draggable="true">
                <div class="song-lib-info">
                    <div class="song-lib-title">${song.title}</div>
                    <div class="song-lib-meta">${song.artist || 'Inconnu'} &bull; ${song.pages || '?'}p
                        ${song.source ? ' &bull; ' + song.source : ''}
                    </div>
                </div>
                <button class="btn-add-song" data-id="${song.id}" title="Ajouter">+</button>
            </div>
        `).join('');

        // Bind add buttons
        list.querySelectorAll('.btn-add-song').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.addSong(parseInt(btn.dataset.id));
            });
        });

        // Drag from library
        list.querySelectorAll('.song-library-item[draggable]').forEach(item => {
            item.addEventListener('dragstart', (e) => {
                e.dataTransfer.effectAllowed = 'copy';
                e.dataTransfer.setData('application/song-id', item.dataset.id);
                e.dataTransfer.setData('source', 'library');
            });
        });
    },

    renderSelected() {
        const list = document.getElementById('songSelectedList');
        if (!list) return;

        if (BB.state.bookSongs.length === 0) {
            list.innerHTML = '<p class="empty-state" style="padding: 1rem;">Glissez des morceaux ici ou cliquez "+"</p>';
            this.updateNextButton();
            this.updateCounters();
            return;
        }

        list.innerHTML = BB.state.bookSongs.map((song, i) => `
            <div class="song-selected-item" data-id="${song.id}" data-index="${i}" draggable="true">
                <input type="checkbox" class="song-check" data-index="${i}">
                <span class="song-position">${i + 1}.</span>
                <div class="song-sel-info">
                    <div class="song-sel-title">${song.title}</div>
                    <div class="song-sel-meta">${song.artist || 'Inconnu'} &bull; ${song.pages || '?'}p</div>
                </div>
            </div>
        `).join('');

        this._attachReorderHandlers();
        this.updateNextButton();
        this.updateCounters();
    },

    updateCounters() {
        const countEl = document.getElementById('step1SongCount');
        const pagesEl = document.getElementById('step1PageCount');
        if (countEl) countEl.textContent = BB.state.bookSongs.length;
        if (pagesEl) {
            const pages = BB.state.bookSongs.reduce((s, song) => s + (song.pages || 1), 0);
            pagesEl.textContent = pages;
        }
    },

    updateNextButton() {
        const btn = document.getElementById('btnStep1Next');
        if (btn) btn.disabled = BB.state.bookSongs.length === 0;
    },

    async addSong(songId) {
        if (!BB.state.currentBook) return;
        try {
            await BB.api(`/books/${BB.state.currentBook.id}/add_song`, {
                method: 'POST',
                body: JSON.stringify({ song_id: songId })
            });
            await BB.loadBookSongs();
            BB.state.allBooks = await BB.api('/books');
            BB.modules.sidebar?.renderBookList();
            this.renderLibrary();
            this.renderSelected();
        } catch (error) {
            BB.notify(error.message || 'Erreur ajout morceau', 'error');
        }
    },

    async addAllVisible() {
        if (!BB.state.currentBook) return;
        const bookSongIds = new Set(BB.state.bookSongs.map(s => s.id));
        const toAdd = BB.state.availableSongs.filter(s => !bookSongIds.has(s.id));

        for (const song of toAdd) {
            try {
                await BB.api(`/books/${BB.state.currentBook.id}/add_song`, {
                    method: 'POST',
                    body: JSON.stringify({ song_id: song.id })
                });
            } catch (e) {
                // Skip incompatible songs
            }
        }

        await BB.loadBookSongs();
        BB.state.allBooks = await BB.api('/books');
        BB.modules.sidebar?.renderBookList();
        this.renderLibrary();
        this.renderSelected();
        BB.notify(`${toAdd.length} morceaux ajoutes`);
    },

    _getCheckedIndices() {
        const checks = document.querySelectorAll('#songSelectedList .song-check:checked');
        return Array.from(checks).map(c => parseInt(c.dataset.index));
    },

    async moveSelected(direction) {
        const indices = this._getCheckedIndices();
        if (indices.length === 0) return;

        const songs = BB.state.bookSongs;
        // Sort indices for proper moving
        indices.sort((a, b) => direction < 0 ? a - b : b - a);

        for (const idx of indices) {
            const newIdx = idx + direction;
            if (newIdx < 0 || newIdx >= songs.length) continue;
            [songs[idx], songs[newIdx]] = [songs[newIdx], songs[idx]];
        }

        this.renderSelected();
        await this._persistOrder();
    },

    async removeChecked() {
        const indices = this._getCheckedIndices();
        if (indices.length === 0) return;

        const toRemove = indices.map(i => BB.state.bookSongs[i]).filter(Boolean);
        for (const song of toRemove) {
            try {
                await BB.api(`/books/${BB.state.currentBook.id}/remove_song/${song.id}`, {
                    method: 'DELETE'
                });
            } catch (e) { /* ignore */ }
        }

        await BB.loadBookSongs();
        BB.state.allBooks = await BB.api('/books');
        BB.modules.sidebar?.renderBookList();
        this.renderLibrary();
        this.renderSelected();
    },

    async clearAll() {
        if (BB.state.bookSongs.length === 0) return;
        if (!confirm('Retirer tous les morceaux du book ?')) return;

        for (const song of [...BB.state.bookSongs]) {
            try {
                await BB.api(`/books/${BB.state.currentBook.id}/remove_song/${song.id}`, {
                    method: 'DELETE'
                });
            } catch (e) { /* ignore */ }
        }

        await BB.loadBookSongs();
        BB.state.allBooks = await BB.api('/books');
        BB.modules.sidebar?.renderBookList();
        this.renderLibrary();
        this.renderSelected();
    },

    async _persistOrder() {
        if (!BB.state.currentBook) return;
        const songIds = BB.state.bookSongs.map(s => s.id);
        try {
            await BB.api(`/books/${BB.state.currentBook.id}/reorder`, {
                method: 'POST',
                body: JSON.stringify({ song_ids: songIds })
            });
        } catch (error) {
            BB.notify('Erreur reordonnancement', 'error');
        }
    },

    _attachReorderHandlers() {
        const list = document.getElementById('songSelectedList');
        if (!list) return;
        let draggedItem = null;

        // Drop zone for library items
        list.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = draggedItem ? 'move' : 'copy';
        });

        list.addEventListener('drop', async (e) => {
            e.preventDefault();
            const source = e.dataTransfer.getData('source');
            if (source === 'library') {
                const songId = parseInt(e.dataTransfer.getData('application/song-id'));
                if (songId) await this.addSong(songId);
                return;
            }
            // Internal reorder handled per-item
        });

        // Per-item reorder drag
        list.querySelectorAll('.song-selected-item[draggable]').forEach(item => {
            item.addEventListener('dragstart', (e) => {
                draggedItem = item;
                item.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', item.dataset.id);
                e.dataTransfer.setData('source', 'selected');
            });

            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
                list.querySelectorAll('.song-selected-item').forEach(el => {
                    el.classList.remove('drag-over-above', 'drag-over-below');
                });
                draggedItem = null;
            });

            item.addEventListener('dragover', (e) => {
                e.preventDefault();
                if (!draggedItem || draggedItem === item) return;
                e.dataTransfer.dropEffect = 'move';
                list.querySelectorAll('.song-selected-item').forEach(el => {
                    el.classList.remove('drag-over-above', 'drag-over-below');
                });
                const rect = item.getBoundingClientRect();
                const mid = rect.top + rect.height / 2;
                item.classList.add(e.clientY < mid ? 'drag-over-above' : 'drag-over-below');
            });

            item.addEventListener('dragleave', () => {
                item.classList.remove('drag-over-above', 'drag-over-below');
            });

            item.addEventListener('drop', async (e) => {
                e.preventDefault();
                e.stopPropagation();
                if (!draggedItem || draggedItem === item) return;

                const fromIdx = parseInt(draggedItem.dataset.index);
                let toIdx = parseInt(item.dataset.index);
                const rect = item.getBoundingClientRect();
                if (e.clientY >= rect.top + rect.height / 2 && toIdx < BB.state.bookSongs.length - 1) {
                    toIdx += 1;
                }

                const [moved] = BB.state.bookSongs.splice(fromIdx, 1);
                if (toIdx > fromIdx) toIdx--;
                BB.state.bookSongs.splice(toIdx, 0, moved);

                this.renderSelected();
                await this._persistOrder();
            });
        });
    }
};

BB.registerModule('step1', step1);

})();
