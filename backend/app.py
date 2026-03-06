"""
Music Book Generator - Application Flask principale
"""

from flask import Flask, render_template
from flask_cors import CORS
from config import Config, ensure_directories
from models.song import db

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Configuration
app.config.from_object(Config)

# CORS
CORS(app)

# Database
db.init_app(app)

# Créer les répertoires nécessaires
ensure_directories()

# Créer les tables
with app.app_context():
    db.create_all()


# Routes principales (pages HTML)
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('catalog.html')


@app.route('/catalog')
def catalog():
    """Page de gestion du catalogue"""
    return render_template('catalog.html')


@app.route('/book-builder')
def book_builder():
    """Page de construction de book"""
    return render_template('book_builder.html')


@app.route('/import')
def import_page():
    """Page d'import de PDF"""
    return render_template('import.html')


@app.route('/settings')
def settings():
    """Page de configuration"""
    return render_template('settings.html')


# Import des routes API
from api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')


if __name__ == '__main__':
    print("=" * 50)
    print("  Music Book Generator")
    print("=" * 50)
    print(f"\n🚀 Serveur démarré sur http://{Config.HOST}:{Config.PORT}")
    print("\n📚 Pages disponibles:")
    print(f"   - Catalogue:     http://localhost:{Config.PORT}/catalog")
    print(f"   - Book Builder:  http://localhost:{Config.PORT}/book-builder")
    print(f"   - Import:        http://localhost:{Config.PORT}/import")
    print("\n   Appuyez sur Ctrl+C pour arrêter\n")

    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
