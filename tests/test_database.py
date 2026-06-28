from pathlib import Path

import database as db


def test_database_round_trip(tmp_path: Path, monkeypatch) -> None:
    test_db = tmp_path / "study.sqlite3"
    monkeypatch.setattr(db, "DB_PATH", test_db)
    owner = "device-a"

    db.init_db()
    document_id = db.insert_document("note.txt", "Clean text", "device-a:hash-1", owner)
    db.insert_study_content(
        document_id,
        {
            "title": "Note",
            "subject": "Computer Science",
            "chapter": "Chapter 1",
            "summary_short": "Short",
            "summary_medium": "Medium",
            "summary_detailed": "Detailed",
            "keywords": ["JavaScript"],
            "key_points": ["Point"],
            "flashcards": [{"question": "Q", "answer": "A"}],
            "mcqs": [{"question": "Q", "options": ["A", "B", "C", "D"], "correct_answer": "A"}],
            "short_questions": ["Explain"],
            "difficulty": "Easy",
            "estimated_study_time": "1 min",
        },
    )
    db.save_progress(document_id, 10, 80, owner)

    content = db.get_content_for_document(document_id, owner)
    progress = db.list_progress(owner)

    assert content is not None
    assert content["keywords"] == ["JavaScript"]
    assert progress[0]["last_score"] == 80


def test_database_filters_documents_by_owner(tmp_path: Path, monkeypatch) -> None:
    test_db = tmp_path / "study.sqlite3"
    monkeypatch.setattr(db, "DB_PATH", test_db)

    db.init_db()
    db.insert_document("mine.txt", "Private text", "device-a:hash", "device-a")
    db.insert_document("friend.txt", "Friend text", "device-b:hash", "device-b")

    mine = db.list_documents("device-a")
    friend = db.list_documents("device-b")

    assert [row["filename"] for row in mine] == ["mine.txt"]
    assert [row["filename"] for row in friend] == ["friend.txt"]
