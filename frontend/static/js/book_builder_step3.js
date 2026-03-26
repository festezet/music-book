/**
 * Book Builder - Step 3 : Export settings
 * Format, orientation, margins, filename pattern
 */
(function() {

const BB = window.BookBuilder;

const MARGIN_PRESETS = {
    standard: { top: 20, bottom: 20, left: 15, right: 15 },
    print:    { top: 25, bottom: 25, left: 20, right: 20 },
    compact:  { top: 10, bottom: 10, left: 10, right: 10 }
};

const step3 = {
    init() {
        this.bindEvents();
    },

    onEnter() {
        this.loadSettings();
        this.updateFilenamePreview();
    },

    onLeave() {
        this.saveSettings();
    },

    bindEvents() {
        document.getElementById('btnStep3Prev')?.addEventListener('click', () => BB.prevStep());
        document.getElementById('btnStep3Next')?.addEventListener('click', () => {
            this.saveSettings();
            BB.nextStep();
        });

        // Margin presets
        document.querySelectorAll('.margin-preset').forEach(btn => {
            btn.addEventListener('click', () => {
                const preset = MARGIN_PRESETS[btn.dataset.preset];
                if (!preset) return;
                document.getElementById('marginTop').value = preset.top;
                document.getElementById('marginBottom').value = preset.bottom;
                document.getElementById('marginLeft').value = preset.left;
                document.getElementById('marginRight').value = preset.right;
            });
        });

        // Filename pattern preview
        document.getElementById('cfgFilenamePattern')?.addEventListener('input', () => {
            this.updateFilenamePreview();
        });
    },

    loadSettings() {
        const book = BB.state.currentBook;
        if (!book) return;

        // Format radio
        const format = book.format || 'A4';
        const fmtRadio = document.querySelector(`input[name="pageFormat"][value="${format}"]`);
        if (fmtRadio) fmtRadio.checked = true;

        // Orientation radio
        const orient = book.orientation || 'portrait';
        const oriRadio = document.querySelector(`input[name="orientation"][value="${orient}"]`);
        if (oriRadio) oriRadio.checked = true;

        // Margins
        document.getElementById('marginTop').value = book.margin_top ?? 20;
        document.getElementById('marginBottom').value = book.margin_bottom ?? 20;
        document.getElementById('marginLeft').value = book.margin_left ?? 15;
        document.getElementById('marginRight').value = book.margin_right ?? 15;

        // Filename pattern
        const patternInput = document.getElementById('cfgFilenamePattern');
        if (patternInput) patternInput.value = book.filename_pattern || '{title}_{instrument}_{date}';
    },

    updateFilenamePreview() {
        const pattern = document.getElementById('cfgFilenamePattern')?.value || '{title}_{instrument}_{date}';
        const book = BB.state.currentBook;
        const preview = pattern
            .replace('{title}', book?.title || 'MonBook')
            .replace('{instrument}', book?.instrument || 'guitar')
            .replace('{date}', new Date().toISOString().slice(0, 10));
        const el = document.getElementById('filenamePreview');
        if (el) el.textContent = preview + '.pdf';
    },

    async saveSettings() {
        const data = {
            format: document.querySelector('input[name="pageFormat"]:checked')?.value || 'A4',
            orientation: document.querySelector('input[name="orientation"]:checked')?.value || 'portrait',
            margin_top: parseInt(document.getElementById('marginTop')?.value) || 20,
            margin_bottom: parseInt(document.getElementById('marginBottom')?.value) || 20,
            margin_left: parseInt(document.getElementById('marginLeft')?.value) || 15,
            margin_right: parseInt(document.getElementById('marginRight')?.value) || 15,
            filename_pattern: document.getElementById('cfgFilenamePattern')?.value || '{title}_{instrument}_{date}'
        };
        await BB.saveBookSettings(data);
    }
};

BB.registerModule('step3', step3);

})();
