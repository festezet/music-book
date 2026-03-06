#!/bin/bash

# Music Book Generator - Lanceur GUI
# Lance l'interface Tkinter

PROJECT_DIR="/data/projects/music-book"

echo "========================================="
echo "  Music Book Generator - GUI"
echo "========================================="
echo ""

cd "$PROJECT_DIR" || exit 1

# Vérifier Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier les dépendances
echo "🔍 Vérification des dépendances..."
python3 -c "import tkinter" 2>/dev/null || {
    echo "❌ Tkinter n'est pas installé"
    echo "   Installez avec: sudo apt install python3-tk"
    exit 1
}

python3 -c "import flask" 2>/dev/null || {
    echo "❌ Flask n'est pas installé"
    echo "   Installez les dépendances avec: pip install -r requirements.txt"
    exit 1
}

echo "✅ Dépendances OK"
echo ""

# Lancement
echo "🚀 Lancement de Music Book Generator..."
echo ""

python3 music_book_gui.py

echo ""
echo "👋 Application fermée"
