/**
 * Book Builder - Step 2 : Configuration
 * Cover, TOC, Index, Page numbering
 */
(function() {

const BB = window.BookBuilder;

const step2 = {
    init() {
        this.bindEvents();
    },

    onEnter() {
        this.loadSettings();
    },

    onLeave() {
        this.saveSettings();
    },

    bindEvents() {
        document.getElementById('btnStep2Prev')?.addEventListener('click', () => BB.prevStep());
        document.getElementById('btnStep2Next')?.addEventListener('click', () => {
            this.saveSettings();
            BB.nextStep();
        });

        // Toggle page number position visibility
        document.getElementById('cfgPageNumbers')?.addEventListener('change', (e) => {
            const posGroup = document.getElementById('pageNumPositionGroup');
            if (posGroup) posGroup.style.display = e.target.checked ? 'block' : 'none';
        });
    },

    loadSettings() {
        const book = BB.state.currentBook;
        if (!book) return;

        this._setChecked('cfgCover', book.include_cover);
        this._setChecked('cfgToc', book.include_toc);
        this._setChecked('cfgIndexTitle', book.include_index_title);
        this._setChecked('cfgIndexArtist', book.include_index_artist);
        this._setChecked('cfgIndexGenre', book.include_index_genre);
        this._setChecked('cfgPageNumbers', book.page_numbers);

        // Page number position radios
        const pos = book.page_number_position || 'center';
        const radio = document.querySelector(`input[name="pageNumPosition"][value="${pos}"]`);
        if (radio) radio.checked = true;

        // Footer text
        const footerInput = document.getElementById('cfgFooterText');
        if (footerInput) footerInput.value = book.footer_text || 'Music Book';

        // Show/hide position group
        const posGroup = document.getElementById('pageNumPositionGroup');
        if (posGroup) posGroup.style.display = book.page_numbers ? 'block' : 'none';
    },

    async saveSettings() {
        const data = {
            include_cover: this._isChecked('cfgCover'),
            include_toc: this._isChecked('cfgToc'),
            include_index_title: this._isChecked('cfgIndexTitle'),
            include_index_artist: this._isChecked('cfgIndexArtist'),
            include_index_genre: this._isChecked('cfgIndexGenre'),
            page_numbers: this._isChecked('cfgPageNumbers'),
            page_number_position: document.querySelector('input[name="pageNumPosition"]:checked')?.value || 'center',
            footer_text: document.getElementById('cfgFooterText')?.value || 'Music Book'
        };
        await BB.saveBookSettings(data);
    },

    _setChecked(id, value) {
        const el = document.getElementById(id);
        if (el) el.checked = !!value;
    },

    _isChecked(id) {
        return document.getElementById(id)?.checked || false;
    }
};

BB.registerModule('step2', step2);

})();
