# Feature Specification: Offline Smart Study Assistant

## User Story

As a student with lecture notes, exam material, and screenshots, I want an offline CPU-only app that converts my unstructured study material into structured revision resources so I can study without internet access or cloud AI.

## Goals

- Run core processing with Wi-Fi off.
- Use CPU-only inference.
- Accept PDF, TXT, PNG, and JPG input.
- Produce summaries, keywords, key points, flashcards, MCQs, short-answer questions, difficulty, and estimated study time.
- Store extracted text and generated content in SQLite.
- Reuse cached output for repeated uploads.
- Provide search over previous notes.

## Non-Goals

- Cloud APIs or hosted AI services.
- GPU/CUDA acceleration.
- Multi-user authentication for the hackathon MVP.
- Perfect handwriting OCR for every language.
- Mobile APK in Phase 1.

## Functional Requirements

1. The system shall accept PDF, TXT, PNG, and JPG uploads.
2. The system shall extract text from PDF and TXT files locally.
3. The system shall run OCR locally for image files when Tesseract is installed.
4. The system shall clean extracted text before generation.
5. The system shall generate structured JSON matching the study content contract.
6. The system shall store documents and generated content in SQLite.
7. The system shall detect duplicate uploads using a content hash.
8. The system shall show previous sessions in a dashboard.
9. The system shall search prior uploads offline.
10. The system shall provide a progress view for quiz attempts, scores, and per-document completion.

## Non-Functional Requirements

- Startup should be fast enough for a hackathon demo.
- CPU inference must be configurable for low-memory laptops.
- Failures must show human-readable Streamlit errors.
- All core code must be open source and local.
- Repository must use a strong copyleft license.

## Success Metrics

- Demo works with Wi-Fi disabled.
- Sample text produces at least 10 MCQs.
- Search returns a previous upload by keyword.
- Re-uploading the same file avoids regeneration.
- No code references cloud AI APIs.

## Risks

- Local GGUF model file may be too large for repository storage.
- Tesseract installation differs across operating systems.
- CPU inference speed varies by laptop.
- LLM JSON output may be malformed and needs fallback repair.
