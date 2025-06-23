from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional


def _ensure_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_name TEXT NOT NULL,
            text TEXT NOT NULL
        )
        """
    )
    return conn


def add_comment(db_path: str | Path, image_name: str, text: str) -> None:
    """Insert a new comment into the database."""
    with _ensure_db(Path(db_path)) as conn:
        conn.execute(
            "INSERT INTO comments (image_name, text) VALUES (?, ?)",
            (image_name, text),
        )
        conn.commit()


def list_comments(db_path: str | Path, image_name: Optional[str] = None) -> List[Dict[str, str]]:
    """Return all comments or those for a given image."""
    with _ensure_db(Path(db_path)) as conn:
        if image_name:
            cur = conn.execute(
                "SELECT id, image_name, text FROM comments WHERE image_name = ?",
                (image_name,),
            )
        else:
            cur = conn.execute("SELECT id, image_name, text FROM comments")
        rows = cur.fetchall()
    return [
        {"id": r[0], "image_name": r[1], "text": r[2]} for r in rows
    ]


def update_comment(db_path: str | Path, comment_id: int, new_text: str) -> None:
    """Update the text of an existing comment."""
    with _ensure_db(Path(db_path)) as conn:
        conn.execute(
            "UPDATE comments SET text = ? WHERE id = ?",
            (new_text, comment_id),
        )
        conn.commit()
