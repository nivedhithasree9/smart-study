from pathlib import Path

import database as db


def test_database_round_trip(tmp_path: Path, monkeypatch) -> None:
    test_db = tmp_path / "study.sqlite3"
    monkeypatch.setattr(db, "DB_PATH", test_db)

    db.init_db()
    document_id = db.insert_document("note.txt", "Clean text", "hash-1")
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
    db.save_progress(document_id, 10, 80)

    content = db.get_content_for_document(document_id)
    progress = db.list_progress()

    assert content is not None
    assert content["keywords"] == ["JavaScript"]
    assert progress[0]["last_score"] == 80
