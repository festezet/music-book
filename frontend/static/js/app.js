/**
 * Music Book Generator - JavaScript principal
 */

const API_BASE = '/api';

/**
 * Fetch wrapper avec gestion d'erreurs
 */
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: 'Unknown error' }));
            throw new Error(error.error || `HTTP ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

/**
 * Afficher une notification
 */
function showNotification(message, type = 'info') {
    // Simple alert pour l'instant (à améliorer avec un système de toast)
    console.log(`[${type.toUpperCase()}] ${message}`);
    if (type === 'error') {
        alert(`Erreur: ${message}`);
    }
}

/**
 * Formater un label d'instrument
 */
function formatInstrument(instrument) {
    const labels = {
        'guitar': 'Guitare',
        'bass': 'Basse',
        'violin': 'Violon'
    };
    return labels[instrument] || instrument;
}

/**
 * Formater un label de difficulté
 */
function formatDifficulty(difficulty) {
    const labels = {
        'easy': 'Facile',
        'medium': 'Moyen',
        'advanced': 'Avancé'
    };
    return labels[difficulty] || difficulty;
}

/**
 * Debounce function (pour search)
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export des fonctions pour utilisation dans les autres scripts
window.MusicBookApp = {
    apiRequest,
    showNotification,
    formatInstrument,
    formatDifficulty,
    debounce
};
