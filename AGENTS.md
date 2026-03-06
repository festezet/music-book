# AGENTS.md

## Project Overview

**Music Book Generator** is a web application for creating structured music books from PDF sheet music. It generates multi-instrument versions (Guitar, Bass, Violin) with automatic table of contents, page numbering, and alphabetical index.

## Key Facts

- **Author**: Fabrice Estezet
- **Stack**: Python 3, Flask, PyPDF2/pypdf, reportlab, SQLite, JavaScript
- **License**: Personal use
- **Status**: Production (v0.3.0)

## Architecture

```
backend/app.py              → Flask application entry point
backend/models/             → SQLAlchemy models (Song, Book)
backend/services/           → PDF parsing, generation, catalog management
backend/api/                → REST API endpoints
frontend/templates/         → Jinja2 templates (catalog, book builder)
frontend/static/            → CSS + JavaScript (drag-and-drop UI)
scripts/                    → Import and test data generation utilities
```

## Workflow

1. Upload PDF sheet music to catalog with metadata (title, artist, key, difficulty, instruments)
2. Build a book by selecting and ordering songs via drag-and-drop
3. Generate 3 instrument-specific PDF books in one click

## API Endpoints

- `GET/POST /api/catalog` - Song catalog management
- `GET/POST /api/books` - Book creation and listing
- `POST /api/books/<id>/generate` - Generate PDF books
- `POST /api/import/pdf` - PDF upload
- `GET /api/export/catalog` - Catalog export

## Skills Demonstrated

- PDF manipulation (parsing, merging, generation) with PyPDF2 and reportlab
- Full-stack Flask application with SQLAlchemy
- Drag-and-drop UI with vanilla JavaScript
- Multi-output generation pipeline (1 input -> 3 outputs)
- Performance optimization (10x speedup via widget recycling)
