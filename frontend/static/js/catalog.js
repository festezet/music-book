/**
 * Catalog page - Gestion du catalogue de morceaux
 */

const { apiRequest, showNotification, formatInstrument, formatDifficulty, debounce } = window.MusicBookApp;

let currentSongs = [];
let currentFilters = {
    search: '',
    instrument: '',
    difficulty: ''
};

// Elements DOM
const catalogGrid = document.getElementById('catalogGrid');
const searchInput = document.getElementById('searchInput');
const filterInstrument = document.getElementById('filterInstrument');
const filterDifficulty = document.getElementById('filterDifficulty');
const btnClearFilters = document.getElementById('btnClearFilters');
const btnAddSong = document.getElementById('btnAddSong');
const songModal = document.getElementById('songModal');
const songForm = document.getElementById('songForm');
const btnCancelModal = document.getElementById('btnCancelModal');
const closeModal = document.querySelector('.close');

/**
 * Charger le catalogue
 */
async function loadCatalog() {
    try {
        const params = new URLSearchParams();
        if (currentFilters.instrument) params.append('instrument', currentFilters.instrument);
        if (currentFilters.difficulty) params.append('difficulty', currentFilters.difficulty);
        if (currentFilters.search) params.append('search', currentFilters.search);

        const endpoint = params.toString() ? `/catalog?${params}` : '/catalog';
        currentSongs = await apiRequest(endpoint);

        renderCatalog();
    } catch (error) {
        showNotification('Erreur lors du chargement du catalogue', 'error');
    }
}

/**
 * Afficher le catalogue
 */
function renderCatalog() {
    if (currentSongs.length === 0) {
        catalogGrid.innerHTML = '<p class="empty-state">Aucun morceau trouvé. Ajoutez-en un !</p>';
        return;
    }

    catalogGrid.innerHTML = currentSongs.map(song => `
        <div class="song-card" data-id="${song.id}">
            <h3>${song.title}</h3>
            <p class="artist">${song.artist || 'Artiste inconnu'}</p>
            <div class="metadata">
                ${song.key ? `<span class="badge">Tonalité: ${song.key}</span>` : ''}
                ${song.difficulty ? `<span class="badge">${formatDifficulty(song.difficulty)}</span>` : ''}
                ${song.pages ? `<span class="badge">${song.pages} page(s)</span>` : ''}
            </div>
            <div class="metadata" style="margin-top: 0.5rem;">
                ${(song.instruments || []).map(inst =>
                    `<span class="badge" style="background-color: #dbeafe;">${formatInstrument(inst)}</span>`
                ).join('')}
            </div>
        </div>
    `).join('');

    // Event listeners pour les cartes
    document.querySelectorAll('.song-card').forEach(card => {
        card.addEventListener('click', () => {
            const songId = parseInt(card.dataset.id);
            editSong(songId);
        });
    });
}

/**
 * Ouvrir le modal pour ajouter un morceau
 */
function openAddSongModal() {
    document.getElementById('modalTitle').textContent = 'Ajouter un morceau';
    songForm.reset();
    document.getElementById('songId').value = '';
    songModal.style.display = 'flex';
}

/**
 * Éditer un morceau
 */
async function editSong(songId) {
    try {
        const song = await apiRequest(`/catalog/${songId}`);

        document.getElementById('modalTitle').textContent = 'Modifier le morceau';
        document.getElementById('songId').value = song.id;
        document.getElementById('title').value = song.title;
        document.getElementById('artist').value = song.artist || '';
        document.getElementById('key').value = song.key || '';
        document.getElementById('tempo').value = song.tempo || '';
        document.getElementById('genre').value = song.genre || '';
        document.getElementById('difficulty').value = song.difficulty || '';
        document.getElementById('pages').value = song.pages || '';
        document.getElementById('notes').value = song.notes || '';

        // Instruments (checkboxes)
        document.querySelectorAll('input[name="instruments"]').forEach(checkbox => {
            checkbox.checked = (song.instruments || []).includes(checkbox.value);
        });

        songModal.style.display = 'flex';
    } catch (error) {
        showNotification('Erreur lors du chargement du morceau', 'error');
    }
}

/**
 * Fermer le modal
 */
function closeModalFunc() {
    songModal.style.display = 'none';
}

/**
 * Sauvegarder un morceau
 */
async function saveSong(e) {
    e.preventDefault();

    const songId = document.getElementById('songId').value;
    const instruments = Array.from(document.querySelectorAll('input[name="instruments"]:checked'))
        .map(cb => cb.value);

    const data = {
        title: document.getElementById('title').value,
        artist: document.getElementById('artist').value,
        key: document.getElementById('key').value,
        tempo: parseInt(document.getElementById('tempo').value) || null,
        genre: document.getElementById('genre').value,
        difficulty: document.getElementById('difficulty').value,
        instruments: instruments,
        pages: parseInt(document.getElementById('pages').value) || null,
        notes: document.getElementById('notes').value,
        pdf_path: `/data/projects/music-book/data/pdfs/placeholder_${Date.now()}.pdf` // Placeholder
    };

    try {
        if (songId) {
            // Update
            await apiRequest(`/catalog/${songId}`, {
                method: 'PUT',
                body: JSON.stringify(data)
            });
            showNotification('Morceau mis à jour');
        } else {
            // Create
            await apiRequest('/catalog', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showNotification('Morceau ajouté');
        }

        closeModalFunc();
        loadCatalog();
    } catch (error) {
        showNotification('Erreur lors de la sauvegarde', 'error');
    }
}

/**
 * Filtres
 */
searchInput.addEventListener('input', debounce(() => {
    currentFilters.search = searchInput.value;
    loadCatalog();
}, 300));

filterInstrument.addEventListener('change', () => {
    currentFilters.instrument = filterInstrument.value;
    loadCatalog();
});

filterDifficulty.addEventListener('change', () => {
    currentFilters.difficulty = filterDifficulty.value;
    loadCatalog();
});

btnClearFilters.addEventListener('click', () => {
    searchInput.value = '';
    filterInstrument.value = '';
    filterDifficulty.value = '';
    currentFilters = { search: '', instrument: '', difficulty: '' };
    loadCatalog();
});

/**
 * Modal events
 */
btnAddSong.addEventListener('click', openAddSongModal);
btnCancelModal.addEventListener('click', closeModalFunc);
closeModal.addEventListener('click', closeModalFunc);
songForm.addEventListener('submit', saveSong);

// Fermer le modal en cliquant en dehors
songModal.addEventListener('click', (e) => {
    if (e.target === songModal) {
        closeModalFunc();
    }
});

// Chargement initial
document.addEventListener('DOMContentLoaded', loadCatalog);
