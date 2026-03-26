/**
 * Book Builder - Orchestrateur workflow 4 etapes
 * Gere la navigation entre steps, l'etat global et l'init
 */
(function() {

const { apiRequest, showNotification, formatInstrument, debounce } = window.MusicBookApp;

// ==============================================
// STATE GLOBAL
// ==============================================
window.BookBuilder = {
    state: {
        currentBook: null,
        bookSongs: [],
        allBooks: [],
        availableSongs: [],
        currentStep: 1,
        catalogFilters: { sources: [], genres: [], artists: [] },
        contextMenuBookId: null
    },

    // Shared utilities
    api: apiRequest,
    notify: showNotification,
    formatInstrument: formatInstrument,
    debounce: debounce,

    // Module registry
    modules: {},

    registerModule(name, mod) {
        this.modules[name] = mod;
    }
};

const BB = window.BookBuilder;

// ==============================================
// WORKFLOW NAVIGATION
// ==============================================

BB.goToStep = function(step) {
    if (step < 1 || step > 4) return;
    if (!BB.state.currentBook && step > 0) {
        BB.notify('Selectionnez ou creez un book d\'abord', 'error');
        return;
    }

    // Save current step data before navigating
    const prevStep = BB.state.currentStep;
    if (prevStep !== step && BB.modules[`step${prevStep}`]?.onLeave) {
        BB.modules[`step${prevStep}`].onLeave();
    }

    BB.state.currentStep = step;

    // Show/hide step panels
    for (let i = 1; i <= 4; i++) {
        const panel = document.getElementById(`step${i}`);
        if (panel) panel.style.display = i === step ? 'block' : 'none';
    }

    // Update step indicators
    document.querySelectorAll('.workflow-step').forEach(el => {
        const s = parseInt(el.dataset.step);
        el.classList.remove('current', 'completed');
        if (s === step) el.classList.add('current');
        else if (s < step) el.classList.add('completed');
    });

    // Notify entering module
    if (BB.modules[`step${step}`]?.onEnter) {
        BB.modules[`step${step}`].onEnter();
    }
};

BB.nextStep = function() {
    BB.goToStep(BB.state.currentStep + 1);
};

BB.prevStep = function() {
    BB.goToStep(BB.state.currentStep - 1);
};

// ==============================================
// BOOK SELECTION (called from sidebar)
// ==============================================

BB.selectBook = async function(bookId) {
    try {
        BB.state.currentBook = await BB.api(`/books/${bookId}`);
        await BB.loadBookSongs();
        if (BB.modules.sidebar) BB.modules.sidebar.renderBookList();
        BB.goToStep(1);
    } catch (error) {
        BB.notify('Erreur lors du chargement du book', 'error');
    }
};

BB.loadBookSongs = async function() {
    if (!BB.state.currentBook) return;
    try {
        const response = await BB.api(`/books/${BB.state.currentBook.id}/songs`);
        BB.state.bookSongs = response.map(bs => bs.song);
    } catch (error) {
        BB.notify('Erreur chargement morceaux du book', 'error');
    }
};

// Save book settings to backend
BB.saveBookSettings = async function(data) {
    if (!BB.state.currentBook) return;
    try {
        const updated = await BB.api(`/books/${BB.state.currentBook.id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
        Object.assign(BB.state.currentBook, updated);
    } catch (error) {
        BB.notify('Erreur de sauvegarde', 'error');
    }
};

// ==============================================
// LOAD CATALOG FILTERS
// ==============================================

BB.loadCatalogFilters = async function() {
    try {
        BB.state.catalogFilters = await BB.api('/catalog/filters');
    } catch (error) {
        console.error('Failed to load catalog filters:', error);
    }
};

// ==============================================
// INITIALIZATION
// ==============================================

document.addEventListener('DOMContentLoaded', async () => {
    // Apply dark theme
    document.body.classList.add('dark-theme');

    // Load initial data
    await Promise.all([
        BB.loadCatalogFilters(),
        (async () => {
            try {
                BB.state.allBooks = await BB.api('/books');
            } catch (e) {
                console.error('Failed to load books:', e);
            }
        })()
    ]);

    // Init all modules
    Object.values(BB.modules).forEach(mod => {
        if (mod.init) mod.init();
    });

    // Workflow step click navigation
    document.querySelectorAll('.workflow-step').forEach(el => {
        el.addEventListener('click', () => {
            const step = parseInt(el.dataset.step);
            if (BB.state.currentBook) BB.goToStep(step);
        });
    });

    // Start at step 1, no book selected
    for (let i = 1; i <= 4; i++) {
        const panel = document.getElementById(`step${i}`);
        if (panel) panel.style.display = i === 1 ? 'block' : 'none';
    }
});

})();
