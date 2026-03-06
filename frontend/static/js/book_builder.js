/**
 * Book Builder page - Construction de music books
 */

const { apiRequest, showNotification, formatInstrument } = window.MusicBookApp;

let availableSongs = [];
let currentBook = null;
let bookSongs = [];

// Elements DOM
const availableSongsList = document.getElementById('availableSongsList');
const bookSongsList = document.getElementById('bookSongsList');
const btnNewBook = document.getElementById('btnNewBook');
const btnSaveBook = document.getElementById('btnSaveBook');
const btnGenerateBook = document.getElementById('btnGenerateBook');
const newBookModal = document.getElementById('newBookModal');
const newBookForm = document.getElementById('newBookForm');
const btnCancelNewBook = document.getElementById('btnCancelNewBook');
const closeNewBookModal = document.querySelector('#newBookModal .close');
const searchSongs = document.getElementById('searchSongs');
const filterInstrumentBuilder = document.getElementById('filterInstrumentBuilder');

/**
 * Charger les morceaux disponibles
 */
async function loadAvailableSongs() {
    try {
        const params = new URLSearchParams();
        const search = searchSongs.value;
        const instrument = filterInstrumentBuilder.value;

        if (search) params.append('search', search);
        if (instrument) params.append('instrument', instrument);

        const endpoint = params.toString() ? `/catalog?${params}` : '/catalog';
        availableSongs = await apiRequest(endpoint);

        renderAvailableSongs();
    } catch (error) {
        showNotification('Erreur lors du chargement des morceaux', 'error');
    }
}

/**
 * Afficher les morceaux disponibles
 */
function renderAvailableSongs() {
    if (availableSongs.length === 0) {
        availableSongsList.innerHTML = '<p class="empty-state">Aucun morceau disponible</p>';
        return;
    }

    availableSongsList.innerHTML = availableSongs.map(song => `
        <div class="song-item" draggable="true" data-id="${song.id}">
            <strong>${song.title}</strong>
            <div style="font-size: 0.875rem; color: #64748b;">
                ${song.artist || 'Artiste inconnu'} • ${song.pages || '?'} page(s)
                <br>
                ${(song.instruments || []).map(inst => formatInstrument(inst)).join(', ')}
            </div>
        </div>
    `).join('');

    // Drag & drop events
    document.querySelectorAll('.song-item').forEach(item => {
        item.addEventListener('dragstart', handleDragStart);
    });
}

/**
 * Créer un nouveau book
 */
async function createNewBook(e) {
    e.preventDefault();

    const data = {
        title: document.getElementById('bookTitleInput').value,
        instrument: document.getElementById('bookInstrumentInput').value,
        include_cover: document.querySelector('input[name="include_cover"]').checked,
        include_toc: document.querySelector('input[name="include_toc"]').checked,
        include_index: document.querySelector('input[name="include_index"]').checked
    };

    try {
        currentBook = await apiRequest('/books', {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showNotification('Book créé avec succès');
        closeNewBookModalFunc();
        updateBookUI();
        loadAvailableSongs(); // Recharger avec le filtre d'instrument
    } catch (error) {
        showNotification('Erreur lors de la création du book', 'error');
    }
}

/**
 * Mettre à jour l'UI du book
 */
function updateBookUI() {
    if (!currentBook) {
        document.getElementById('bookTitle').textContent = 'Sélectionnez ou créez un book';
        document.getElementById('bookInfo').style.display = 'none';
        btnSaveBook.disabled = true;
        btnGenerateBook.disabled = true;
        return;
    }

    document.getElementById('bookTitle').textContent = currentBook.title;
    document.getElementById('bookInstrument').textContent = formatInstrument(currentBook.instrument);
    document.getElementById('bookSongCount').textContent = bookSongs.length;
    document.getElementById('bookPageCount').textContent = calculateTotalPages();
    document.getElementById('bookInfo').style.display = 'block';

    btnSaveBook.disabled = false;
    btnGenerateBook.disabled = bookSongs.length === 0;

    renderBookSongs();
}

/**
 * Calculer le nombre total de pages
 */
function calculateTotalPages() {
    let total = 0;
    if (currentBook.include_cover) total += 1;
    if (currentBook.include_toc) total += 2;
    if (currentBook.include_index) total += 1;
    total += bookSongs.reduce((sum, song) => sum + (song.pages || 1), 0);
    return total;
}

/**
 * Charger les morceaux d'un book
 */
async function loadBookSongs() {
    if (!currentBook) return;

    try {
        const response = await apiRequest(`/books/${currentBook.id}/songs`);
        bookSongs = response.map(bs => bs.song);
        updateBookUI();
    } catch (error) {
        showNotification('Erreur lors du chargement des morceaux du book', 'error');
    }
}

/**
 * Afficher les morceaux du book
 */
function renderBookSongs() {
    if (bookSongs.length === 0) {
        bookSongsList.innerHTML = '<p class="empty-state">Glissez-déposez des morceaux ici</p>';
        return;
    }

    bookSongsList.innerHTML = bookSongs.map((song, index) => `
        <div class="song-item" data-id="${song.id}" data-position="${index}">
            <strong>${index + 1}. ${song.title}</strong>
            <div style="font-size: 0.875rem; color: #64748b;">
                ${song.artist || 'Artiste inconnu'} • ${song.pages || '?'} page(s)
            </div>
            <button class="btn btn-danger" onclick="removeSongFromBook(${song.id})" style="margin-top: 0.5rem; padding: 0.25rem 0.5rem; font-size: 0.75rem;">
                Retirer
            </button>
        </div>
    `).join('');
}

/**
 * Ajouter un morceau au book
 */
async function addSongToBook(songId) {
    if (!currentBook) {
        showNotification('Veuillez d\'abord créer un book', 'error');
        return;
    }

    try {
        await apiRequest(`/books/${currentBook.id}/add_song`, {
            method: 'POST',
            body: JSON.stringify({ song_id: songId })
        });

        // Recharger les morceaux du book
        await loadBookSongs();
        showNotification('Morceau ajouté au book');
    } catch (error) {
        showNotification(error.message || 'Erreur lors de l\'ajout', 'error');
    }
}

/**
 * Retirer un morceau du book
 */
window.removeSongFromBook = async function(songId) {
    if (!currentBook) return;

    try {
        await apiRequest(`/books/${currentBook.id}/remove_song/${songId}`, {
            method: 'DELETE'
        });

        await loadBookSongs();
        showNotification('Morceau retiré du book');
    } catch (error) {
        showNotification('Erreur lors de la suppression', 'error');
    }
};

/**
 * Drag & Drop handlers
 */
function handleDragStart(e) {
    e.dataTransfer.effectAllowed = 'copy';
    e.dataTransfer.setData('text/plain', e.target.dataset.id);
}

bookSongsList.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
    bookSongsList.style.backgroundColor = 'rgba(37, 99, 235, 0.05)';
});

bookSongsList.addEventListener('dragleave', () => {
    bookSongsList.style.backgroundColor = '';
});

bookSongsList.addEventListener('drop', async (e) => {
    e.preventDefault();
    bookSongsList.style.backgroundColor = '';

    const songId = parseInt(e.dataTransfer.getData('text/plain'));
    await addSongToBook(songId);
});

/**
 * Générer les PDF
 */
btnGenerateBook.addEventListener('click', async () => {
    if (!currentBook) return;

    try {
        const result = await apiRequest(`/books/${currentBook.id}/generate`, {
            method: 'POST'
        });

        showNotification('Génération lancée (non implémentée encore)', 'error');
    } catch (error) {
        showNotification('Fonctionnalité non implémentée', 'error');
    }
});

/**
 * Modal events
 */
function closeNewBookModalFunc() {
    newBookModal.style.display = 'none';
}

btnNewBook.addEventListener('click', () => {
    newBookModal.style.display = 'flex';
});

btnCancelNewBook.addEventListener('click', closeNewBookModalFunc);
closeNewBookModal.addEventListener('click', closeNewBookModalFunc);
newBookForm.addEventListener('submit', createNewBook);

newBookModal.addEventListener('click', (e) => {
    if (e.target === newBookModal) {
        closeNewBookModalFunc();
    }
});

/**
 * Filtres
 */
searchSongs.addEventListener('input', window.MusicBookApp.debounce(() => {
    loadAvailableSongs();
}, 300));

filterInstrumentBuilder.addEventListener('change', loadAvailableSongs);

/**
 * Initialisation
 */
document.addEventListener('DOMContentLoaded', () => {
    loadAvailableSongs();
});
