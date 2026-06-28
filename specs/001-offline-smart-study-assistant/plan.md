# Implementation Plan

## Architecture

```text
Streamlit pages
  Dashboard
  Upload Notes
  AI Summary
  Flashcards
  MCQ Generator
  Study History
  Search Notes
  Settings

Services
  pdf_reader.py
  ocr.py
  text_processing.py
  llm.py
  summarizer.py
  flashcards.py
  mcq_generator.py
  keyword_extractor.py
  cache.py
  export.py

Persistence
  SQLite database
  uploads/ for uploaded files
  models/ for local GGUF models
```

## Offline AI Path

- Primary: `llama-cpp-python` loading a local `.gguf` file.
- Prompt asks for strict JSON.
- Parser extracts and validates JSON.
- Deterministic local fallback is allowed only for development resilience and must not call the internet.

## CPU Performance Choices

- Default context window: 2048 tokens.
- Default thread count: detected CPU count or user override.
- Chunk long documents before generation.
- Cache by normalized content hash.
- Avoid loading the model until generation is requested.

## Storage Plan

- `Documents` stores filename, date, extracted text, hash, and bookmark flag.
- `StudyContent` stores all generated structured fields as text/JSON.
- `StudyProgress` stores quiz and flashcard progress events.

## Phase 2 MVP Build Order

1. Finish database and schema initialization.
2. Implement file extraction for TXT, PDF, and images.
3. Implement text cleaning and hashing.
4. Implement local LLM service and JSON fallback.
5. Build Streamlit navigation and upload flow.
6. Render dashboard, summaries, flashcards, MCQs, search, and settings.
7. Add exports and quiz mode.
8. Test offline demo with sample data.

## Phase 3 Audit Plan

Add real checks for:

- Black formatting
- Ruff linting
- Mypy type checking
- Pytest unit tests
- Bandit security scan
- pip-audit dependency scan
- detect-secrets
- Markdown lint
- YAML lint
- License metadata check
- No cloud API string scan
- Streamlit import smoke test
