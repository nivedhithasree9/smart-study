# Data Model

## Documents

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | Auto-increment. |
| filename | TEXT | Original uploaded filename. |
| upload_date | TEXT | UTC ISO timestamp. |
| extracted_text | TEXT | Cleaned local extraction output. |
| content_hash | TEXT UNIQUE | SHA-256 of normalized text. |
| bookmarked | INTEGER | 0 or 1. |

## StudyContent

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | Auto-increment. |
| document_id | INTEGER UNIQUE | Foreign key to Documents. |
| title | TEXT | Generated or inferred title. |
| subject | TEXT | Generated or inferred subject. |
| chapter | TEXT | Generated or inferred chapter. |
| summary_short | TEXT | Brief summary. |
| summary_medium | TEXT | Medium summary. |
| summary_detailed | TEXT | Detailed summary. |
| keywords | TEXT | JSON array. |
| key_points | TEXT | JSON array. |
| flashcards | TEXT | JSON array of question/answer objects. |
| mcqs | TEXT | JSON array of MCQ objects. |
| short_questions | TEXT | JSON array. |
| difficulty | TEXT | Easy, Medium, or Hard. |
| estimated_study_time | TEXT | Human-readable duration. |
| created_at | TEXT | UTC ISO timestamp. |

## StudyProgress

| Field | Type | Notes |
| --- | --- | --- |
| id | INTEGER PRIMARY KEY | Auto-increment. |
| document_id | INTEGER | Foreign key to Documents. |
| completed_flashcards | INTEGER | Count completed. |
| completed_mcqs | INTEGER | Count attempted. |
| last_score | INTEGER | Last quiz score percentage. |
| updated_at | TEXT | UTC ISO timestamp. |
