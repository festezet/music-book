"""
Configuration de l'application Music Book Generator
"""

import os

# Répertoire racine du projet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configuration Flask
class Config:
    """Configuration de base"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True

    # Server
    HOST = '0.0.0.0'
    PORT = 5051

    # Database
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "data", "catalog.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'imports')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max par upload
    ALLOWED_EXTENSIONS = {'pdf'}

    # PDF Storage
    PDF_STORAGE = {
        'guitar': os.path.join(BASE_DIR, 'data', 'pdfs', 'guitar'),
        'bass': os.path.join(BASE_DIR, 'data', 'pdfs', 'bass'),
        'violin': os.path.join(BASE_DIR, 'data', 'pdfs', 'violin')
    }

    # Generated books
    GENERATED_FOLDER = os.path.join(BASE_DIR, 'data', 'generated')

    # Export
    EXPORT_FOLDER = os.path.join(BASE_DIR, 'data', 'exports')

    # Instruments
    INSTRUMENTS = ['guitar', 'bass', 'violin']
    INSTRUMENT_LABELS = {
        'guitar': 'Guitare',
        'bass': 'Basse',
        'violin': 'Violon'
    }

    # Difficulty levels
    DIFFICULTY_LEVELS = ['easy', 'medium', 'advanced']
    DIFFICULTY_LABELS = {
        'easy': 'Facile',
        'medium': 'Moyen',
        'advanced': 'Avancé'
    }

    # PDF Generation
    PAGE_FORMAT = 'A4'
    PAGE_ORIENTATION = 'portrait'


def ensure_directories():
    """Créer les répertoires nécessaires s'ils n'existent pas"""
    directories = [
        Config.UPLOAD_FOLDER,
        Config.GENERATED_FOLDER,
        Config.EXPORT_FOLDER,
    ]

    # Ajouter les dossiers par instrument
    directories.extend(Config.PDF_STORAGE.values())

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
