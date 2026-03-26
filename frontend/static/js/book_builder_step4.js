/**
 * Book Builder - Step 4 : Generation
 * Summary, generate PDF, progress, download
 */
(function() {

const BB = window.BookBuilder;

const step4 = {
    init() {
        this.bindEvents();
    },

    onEnter() {
        this.renderSummary();
        this.resetGenerateState();
    },

    bindEvents() {
        document.getElementById('btnStep4Prev')?.addEventListener('click', () => BB.prevStep());
        document.getElementById('btnGenerate')?.addEventListener('click', () => this.generate());
    },

    renderSummary() {
        const book = BB.state.currentBook;
        if (!book) return;

        const tbody = document.getElementById('summaryBody');
        if (!tbody) return;

        const pages = BB.state.bookSongs.reduce((s, song) => s + (song.pages || 1), 0);
        const rows = [
            ['Titre', book.title],
            ['Instrument', BB.formatInstrument(book.instrument)],
            ['Morceaux', `${BB.state.bookSongs.length} (${pages} pages)`],
            ['Page de garde', book.include_cover ? 'Oui' : 'Non'],
            ['Table des matieres', book.include_toc ? 'Oui' : 'Non'],
            ['Index titre', book.include_index_title ? 'Oui' : 'Non'],
            ['Index artiste', book.include_index_artist ? 'Oui' : 'Non'],
            ['Index genre', book.include_index_genre ? 'Oui' : 'Non'],
            ['Numerotation', book.page_numbers ? `Oui (${book.page_number_position || 'center'})` : 'Non'],
            ['Format', book.format || 'A4'],
            ['Orientation', book.orientation || 'portrait'],
            ['Marges (mm)', `${book.margin_top ?? 20} / ${book.margin_bottom ?? 20} / ${book.margin_left ?? 15} / ${book.margin_right ?? 15}`]
        ];

        tbody.innerHTML = rows.map(([label, value]) =>
            `<tr><td>${label}</td><td>${value}</td></tr>`
        ).join('');
    },

    resetGenerateState() {
        const progress = document.getElementById('generateProgress');
        const result = document.getElementById('generateResult');
        if (progress) progress.style.display = 'none';
        if (result) result.style.display = 'none';
    },

    async generate() {
        const book = BB.state.currentBook;
        if (!book) return;

        const btn = document.getElementById('btnGenerate');
        const progress = document.getElementById('generateProgress');
        const result = document.getElementById('generateResult');

        // Show progress
        if (btn) btn.disabled = true;
        if (progress) progress.style.display = 'flex';
        if (result) result.style.display = 'none';

        try {
            const data = await BB.api(`/books/${book.id}/generate`, { method: 'POST' });

            // Update book state with pdf_path
            BB.state.currentBook.pdf_path = data.pdf_path;
            BB.state.allBooks = await BB.api('/books');
            BB.modules.sidebar?.renderBookList();

            // Show result
            if (progress) progress.style.display = 'none';
            if (result) {
                result.style.display = 'block';
                const openBtn = document.getElementById('btnOpenPdf');
                const dlBtn = document.getElementById('btnDownloadPdf');
                if (openBtn) openBtn.onclick = () => window.open(`/api/books/${book.id}/download`, '_blank');
                if (dlBtn) {
                    dlBtn.onclick = () => {
                        const a = document.createElement('a');
                        a.href = `/api/books/${book.id}/download`;
                        a.download = '';
                        a.click();
                    };
                }
            }

            BB.notify('PDF genere avec succes !');
        } catch (error) {
            if (progress) progress.style.display = 'none';
            BB.notify(error.message || 'Erreur lors de la generation', 'error');
        } finally {
            if (btn) btn.disabled = false;
        }
    }
};

BB.registerModule('step4', step4);

})();
