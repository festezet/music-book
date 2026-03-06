#!/bin/bash

# Music Book Generator - Script de lancement
# Port: 5051

PROJECT_DIR="/data/projects/music-book"
BACKEND_DIR="$PROJECT_DIR/backend"
PORT=5051

echo "========================================="
echo "  Music Book Generator"
echo "========================================="
echo ""

# Vérifier que le répertoire backend existe
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Erreur: Le répertoire backend n'existe pas"
    echo "   Chemin: $BACKEND_DIR"
    exit 1
fi

# Vérifier que app.py existe
if [ ! -f "$BACKEND_DIR/app.py" ]; then
    echo "⚠️  Warning: app.py n'existe pas encore"
    echo "   Créez d'abord l'application Flask"
    exit 1
fi

# Vérifier les dépendances Python
echo "🔍 Vérification des dépendances..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "❌ Flask n'est pas installé"
    echo "   Installez les dépendances avec: pip install -r requirements.txt"
    exit 1
fi

# Vérifier que le port n'est pas déjà utilisé
if netstat -tuln | grep -q ":$PORT "; then
    echo "⚠️  Warning: Le port $PORT est déjà utilisé"
    echo "   Arrêtez le processus ou changez le port dans config.py"
    echo ""
    read -p "Continuer quand même ? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Créer la base de données si elle n'existe pas
if [ ! -f "$PROJECT_DIR/data/catalog.db" ]; then
    echo "🗄️  Création de la base de données..."
    python3 -c "
import sys
sys.path.insert(0, '$BACKEND_DIR')
from app import db, app
with app.app_context():
    db.create_all()
print('✅ Base de données créée')
" 2>/dev/null || echo "⚠️  Base de données non créée (app.py doit exister)"
fi

# Lancement du serveur
echo ""
echo "🚀 Lancement du serveur Flask..."
echo "   URL: http://localhost:$PORT"
echo ""
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""

cd "$BACKEND_DIR" || exit 1
python3 app.py

# Si le serveur s'arrête
echo ""
echo "👋 Serveur arrêté"
