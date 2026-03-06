#!/usr/bin/env python3
"""Backup automatique des bases de donnees - music-book"""

import shutil
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent / "data"
BACKUP_DIR = DATA_DIR / "backups"
MAX_BACKUPS = 10

DB_FILES = [
    DATA_DIR / "catalog.db",
]


def backup_database():
    """Backup toutes les DB avec rotation (garde les 10 derniers)."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for db_path in DB_FILES:
        if not db_path.exists():
            continue

        backup_name = f"{db_path.stem}_{timestamp}{db_path.suffix}.bak"
        backup_path = BACKUP_DIR / backup_name
        shutil.copy2(db_path, backup_path)
        print(f"[backup] {db_path.name} -> {backup_name}")

        existing = sorted(
            BACKUP_DIR.glob(f"{db_path.stem}_*{db_path.suffix}.bak"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        for old in existing[MAX_BACKUPS:]:
            old.unlink()
            print(f"[backup] supprime ancien: {old.name}")


if __name__ == "__main__":
    backup_database()
