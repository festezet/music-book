#!/bin/bash
# Music Book Generator - Setup Script

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "========================================="
echo "  Music Book Generator - Setup"
echo "========================================="

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Install it first."
    exit 1
fi

# Create virtualenv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directories
echo "Creating data directories..."
mkdir -p data/pdfs/guitar data/pdfs/bass data/pdfs/violin
mkdir -p data/generated data/exports data/imports data/backups

# Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example - edit it with your settings"
fi

# Initialize database
echo "Initializing database..."
cd backend
python3 -c "
from app import db, app
with app.app_context():
    db.create_all()
print('Database initialized')
"
cd ..

echo ""
echo "Setup complete! Run with: bash start.sh"
