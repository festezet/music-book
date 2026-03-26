/**
 * Book Builder - Sidebar : book list, context menu, CRUD books
 */
(function() {

const BB = window.BookBuilder;

const sidebar = {
    init() {
        this.bindEvents();
        this.renderBookList();
    },

    bindEvents() {
        // New book button
        document.getElementById('btnNewBook').addEventListener('click', () => {
            document.getElementById('newBookModal').style.display = 'flex';
        });

        // Modal close
        document.getElementById('btnCancelNewBook').addEventListener('click', () => {
            document.getElementById('newBookModal').style.display = 'none';
        });
        document.querySelector('#newBookModal .close').addEventListener('click', () => {
            document.getElementById('newBookModal').style.display = 'none';
        });
        document.getElementById('newBookModal').addEventListener('click', (e) => {
            if (e.target.id === 'newBookModal') {
                document.getElementById('newBookModal').style.display = 'none';
            }
        });

        // Create book form
        document.getElementById('newBookForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.createBook();
        });

        // Context menu actions
        document.getElementById('ctxRenameBook').addEventListener('click', () => this.renameBook());
        document.getElementById('ctxDeleteBook').addEventListener('click', () => this.deleteBook());

        // Close context menu on click elsewhere
        document.addEventListener('click', () => {
            document.getElementById('bookContextMenu').style.display = 'none';
        });
    },

    renderBookList() {
        const bookList = document.getElementById('bookList');
        const books = BB.state.allBooks;

        if (books.length === 0) {
            bookList.innerHTML = '<p class="empty-state" style="padding: 1rem; font-size: 0.875rem;">Aucun book. Creez-en un !</p>';
            return;
        }

        const currentId = BB.state.currentBook?.id;
        bookList.innerHTML = books.map(book => `
            <div class="book-list-item ${currentId === book.id ? 'selected' : ''}"
                 data-id="${book.id}">
                <div class="book-item-title">${book.title}</div>
                <div class="book-item-meta">
                    ${BB.formatInstrument(book.instrument)} &bull; ${book.song_count} morceau(x)
                    ${book.pdf_path ? ' &bull; PDF' : ''}
                </div>
            </div>
        `).join('');

        // Bind click + context menu
        bookList.querySelectorAll('.book-list-item').forEach(el => {
            el.addEventListener('click', () => BB.selectBook(parseInt(el.dataset.id)));
            el.addEventListener('contextmenu', (e) => {
                e.preventDefault();
                BB.state.contextMenuBookId = parseInt(el.dataset.id);
                const menu = document.getElementById('bookContextMenu');
                menu.style.display = 'block';
                menu.style.left = e.pageX + 'px';
                menu.style.top = e.pageY + 'px';
            });
        });
    },

    async createBook() {
        const data = {
            title: document.getElementById('bookTitleInput').value,
            instrument: document.getElementById('bookInstrumentInput').value,
        };

        try {
            BB.state.currentBook = await BB.api('/books', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            BB.state.bookSongs = [];
            BB.state.allBooks = await BB.api('/books');
            document.getElementById('newBookModal').style.display = 'none';
            document.getElementById('newBookForm').reset();
            this.renderBookList();
            BB.goToStep(1);
            BB.notify('Book cree avec succes');
        } catch (error) {
            BB.notify('Erreur lors de la creation', 'error');
        }
    },

    async renameBook() {
        const bookId = BB.state.contextMenuBookId;
        if (!bookId) return;
        const book = BB.state.allBooks.find(b => b.id === bookId);
        const newTitle = prompt('Nouveau titre:', book?.title || '');
        if (!newTitle?.trim()) return;

        try {
            await BB.api(`/books/${bookId}`, {
                method: 'PUT',
                body: JSON.stringify({ title: newTitle.trim() })
            });
            BB.state.allBooks = await BB.api('/books');
            if (BB.state.currentBook?.id === bookId) {
                BB.state.currentBook.title = newTitle.trim();
            }
            this.renderBookList();
            BB.notify('Book renomme');
        } catch (error) {
            BB.notify('Erreur lors du renommage', 'error');
        }
    },

    async deleteBook() {
        const bookId = BB.state.contextMenuBookId;
        if (!bookId) return;
        const book = BB.state.allBooks.find(b => b.id === bookId);
        if (!confirm(`Supprimer le book "${book?.title}" ?`)) return;

        try {
            await BB.api(`/books/${bookId}`, { method: 'DELETE' });
            if (BB.state.currentBook?.id === bookId) {
                BB.state.currentBook = null;
                BB.state.bookSongs = [];
            }
            BB.state.allBooks = await BB.api('/books');
            this.renderBookList();
            BB.notify('Book supprime');
        } catch (error) {
            BB.notify('Erreur lors de la suppression', 'error');
        }
    }
};

BB.registerModule('sidebar', sidebar);

})();
