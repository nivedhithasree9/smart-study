# Offline Smart Study Assistant

CPU-first, offline-first study material structuring for students who need useful AI on an ordinary laptop with Wi-Fi off.

## Hackathon Submission

- Event: The CPU-First Hackathon
- Phase: Phase 1, Plan & Spec
- Submission target: before 10:00 AM on June 28, 2026
- App type: Web app with Streamlit
- License: AGPL-3.0-or-later, strong copyleft
- Runtime: Python 3.11+, llama.cpp CPU inference with local GGUF model
- Core guarantee: no cloud APIs, no internet-dependent AI services, no GPU/CUDA requirement

## Problem

Students often have useful study material scattered across PDFs, plain text notes, screenshots, and handwritten images. Turning that material into summaries, flashcards, keywords, MCQs, and revision plans usually requires online AI tools. That fails in classrooms, hostels, rural areas, labs, or exam environments where connectivity is limited or private study data should stay local.

Offline Smart Study Assistant turns unstructured notes into structured study resources entirely on CPU.

## Proposed Solution

The app accepts PDF, TXT, PNG, and JPG uploads, extracts text locally, cleans it, generates study content with a local small language model, stores outputs in SQLite, and lets students search previous uploads offline.

If a local GGUF model is available, the app uses llama.cpp through `llama-cpp-python`. If the model is missing during development, deterministic local extractive generators keep the interface testable without making any network call.

## Model And Runtime Declaration

- Primary model: TinyLlama 1.1B Chat GGUF or Phi-3 Mini GGUF
- Runtime: llama.cpp via `llama-cpp-python`
- Device target: CPU only
- OCR: Tesseract OCR through `pytesseract`
- PDF extraction: PyMuPDF
- Database: SQLite
- Frontend: Streamlit

## Core Features

- Upload study notes as PDF, TXT, PNG, or JPG
- Extract text from PDFs and images
- Clean and normalize extracted text
- Generate short, medium, and detailed summaries
- Extract key points and keywords
- Generate flashcards
- Generate at least 10 MCQs with four options and a correct answer
- Generate short-answer exam questions
- Classify difficulty as Easy, Medium, or Hard
- Estimate reading/study time
- Store documents and generated content in SQLite
- Cache repeated uploads by content hash
- Search previous notes offline
- Bookmark important notes
- Export summaries to PDF and flashcards to CSV

## Offline Demo Plan

1. Install dependencies and place a GGUF model in `models/`.
2. Turn Wi-Fi off.
3. Run `streamlit run app.py`.
4. Upload `sample_data/os_deadlock_notes.txt`.
5. Show generated summaries, flashcards, MCQs, keywords, and stored history.
6. Search for `deadlock` in previous uploads.

## Repository Plan

Phase 1 planning artifacts are in:

- [Spec](specs/001-offline-smart-study-assistant/spec.md)
- [Implementation Plan](specs/001-offline-smart-study-assistant/plan.md)
- [Task Breakdown](specs/001-offline-smart-study-assistant/tasks.md)
- [Data Model](specs/001-offline-smart-study-assistant/data-model.md)
- [JSON Contract](specs/001-offline-smart-study-assistant/contracts/study_content.schema.json)
- [Issue Plan](docs/issues.md)
- [Work Division](docs/work-division.md)

## MVP Architecture

```text
Streamlit UI
  -> upload service
  -> PDF/TXT/OCR extractors
  -> text cleaning
  -> local LLM service, llama.cpp CPU
  -> structured JSON validation
  -> SQLite persistence
  -> dashboard, search, quiz, export
```

## Expected Project Structure

```text
offline-smart-study-assistant/
├── app.py
├── database.py
├── models/
├── services/
├── data/
├── uploads/
├── database/
├── sample_data/
├── specs/
├── docs/
├── requirements.txt
├── LICENSE
└── README.md
```

## Setup Preview

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

On Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Full setup and audit instructions will be completed during Phase 2 and Phase 3.
