"""SQLite persistence for Offline Smart Study Assistant."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path("database/study_assistant.sqlite3")
PRIVACY_SCHEMA_VERSION = 2


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS Documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                upload_date TEXT NOT NULL,
                extracted_text TEXT NOT NULL,
                content_hash TEXT NOT NULL UNIQUE,
                bookmarked INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS StudyContent (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL UNIQUE,
                title TEXT,
                subject TEXT,
                chapter TEXT,
                summary_short TEXT,
                summary_medium TEXT,
                summary_detailed TEXT,
                keywords TEXT,
                key_points TEXT,
                flashcards TEXT,
                mcqs TEXT,
                short_questions TEXT,
                difficulty TEXT,
                estimated_study_time TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(document_id) REFERENCES Documents(id)
            );
            CREATE TABLE IF NOT EXISTS StudyProgress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                completed_flashcards INTEGER NOT NULL DEFAULT 0,
                completed_mcqs INTEGER NOT NULL DEFAULT 0,
                last_score INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(document_id) REFERENCES Documents(id)
            );
            """
        )
        _ensure_owner_columns(conn)


def _ensure_owner_columns(conn: sqlite3.Connection) -> None:
    document_columns = {row["name"] for row in conn.execute("PRAGMA table_info(Documents)").fetchall()}
    progress_columns = {row["name"] for row in conn.execute("PRAGMA table_info(StudyProgress)").fetchall()}
    if "owner_id" not in document_columns:
        conn.execute("ALTER TABLE Documents ADD COLUMN owner_id TEXT NOT NULL DEFAULT 'legacy'")
    if "owner_id" not in progress_columns:
        conn.execute("ALTER TABLE StudyProgress ADD COLUMN owner_id TEXT NOT NULL DEFAULT 'legacy'")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_document_by_hash(hash_value: str, owner_id: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM Documents WHERE content_hash = ? AND owner_id = ?",
            (hash_value, owner_id),
        ).fetchone()


def insert_document(filename: str, extracted_text: str, hash_value: str, owner_id: str) -> int:
    with connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO Documents (filename, upload_date, extracted_text, content_hash, owner_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (filename, utc_now(), extracted_text, hash_value, owner_id),
        )
        return int(cursor.lastrowid)


def insert_study_content(document_id: int, content: dict[str, Any]) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO StudyContent (
                document_id, title, subject, chapter, summary_short, summary_medium,
                summary_detailed, keywords, key_points, flashcards, mcqs,
                short_questions, difficulty, estimated_study_time, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                content["title"],
                content["subject"],
                content["chapter"],
                content["summary_short"],
                content["summary_medium"],
                content["summary_detailed"],
                json.dumps(content["keywords"]),
                json.dumps(content["key_points"]),
                json.dumps(content["flashcards"]),
                json.dumps(content["mcqs"]),
                json.dumps(content["short_questions"]),
                content["difficulty"],
                content["estimated_study_time"],
                utc_now(),
            ),
        )


def row_to_content(row: sqlite3.Row) -> dict[str, Any]:
    content = dict(row)
    for key in ["keywords", "key_points", "flashcards", "mcqs", "short_questions"]:
        content[key] = json.loads(content[key] or "[]")
    return content


def get_content_for_document(document_id: int, owner_id: str) -> dict[str, Any] | None:
    with connect() as conn:
        row = conn.execute(
            """
            SELECT s.*
            FROM StudyContent s JOIN Documents d ON d.id = s.document_id
            WHERE s.document_id = ? AND d.owner_id = ?
            """,
            (document_id, owner_id),
        ).fetchone()
    return row_to_content(row) if row else None


def get_document(document_id: int, owner_id: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM Documents WHERE id = ? AND owner_id = ?",
            (document_id, owner_id),
        ).fetchone()


def update_mcqs(document_id: int, mcqs: list[dict[str, object]], owner_id: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE StudyContent
            SET mcqs = ?, created_at = ?
            WHERE document_id = ? AND EXISTS (
                SELECT 1 FROM Documents d WHERE d.id = StudyContent.document_id AND d.owner_id = ?
            )
            """,
            (json.dumps(mcqs), utc_now(), document_id, owner_id),
        )


def update_flashcards(document_id: int, flashcards: list[dict[str, str]], owner_id: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            UPDATE StudyContent
            SET flashcards = ?, created_at = ?
            WHERE document_id = ? AND EXISTS (
                SELECT 1 FROM Documents d WHERE d.id = StudyContent.document_id AND d.owner_id = ?
            )
            """,
            (json.dumps(flashcards), utc_now(), document_id, owner_id),
        )


def list_documents(owner_id: str) -> list[sqlite3.Row]:
    with connect() as conn:
        return conn.execute(
            """
            SELECT d.*, s.title, s.subject, s.difficulty, s.estimated_study_time
            FROM Documents d LEFT JOIN StudyContent s ON s.document_id = d.id
            WHERE d.owner_id = ?
            ORDER BY d.upload_date DESC
            """,
            (owner_id,),
        ).fetchall()


def search_documents(query: str, owner_id: str) -> list[sqlite3.Row]:
    like = f"%{query}%"
    with connect() as conn:
        return conn.execute(
            """
            SELECT d.*, s.title, s.subject, s.summary_short
            FROM Documents d LEFT JOIN StudyContent s ON s.document_id = d.id
            WHERE d.owner_id = ?
              AND (d.filename LIKE ? OR d.extracted_text LIKE ? OR s.keywords LIKE ? OR s.summary_short LIKE ?)
            ORDER BY d.upload_date DESC
            """,
            (owner_id, like, like, like, like),
        ).fetchall()


def toggle_bookmark(document_id: int, value: bool, owner_id: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE Documents SET bookmarked = ? WHERE id = ? AND owner_id = ?",
            (1 if value else 0, document_id, owner_id),
        )


def save_progress(document_id: int, attempted: int, score: int, owner_id: str) -> None:
    with connect() as conn:
        conn.execute(
            """
            INSERT INTO StudyProgress (document_id, completed_mcqs, last_score, updated_at, owner_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (document_id, attempted, score, utc_now(), owner_id),
        )


def list_progress(owner_id: str) -> list[sqlite3.Row]:
    with connect() as conn:
        return conn.execute(
            """
            SELECT p.*, d.filename
            FROM StudyProgress p JOIN Documents d ON d.id = p.document_id
            WHERE p.owner_id = ?
            ORDER BY p.updated_at DESC
            LIMIT 20
            """,
            (owner_id,),
        ).fetchall()
