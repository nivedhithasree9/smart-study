# Offline Smart Study Assistant

CPU-first, offline-first study material structuring for students who need useful AI on an ordinary laptop with Wi-Fi off.

## Hackathon Submission

- Event: The CPU-First Hackathon
- Phase 2 target: working MVP before lunch on June 28, 2026
- App type: Streamlit web app
- License: AGPL-3.0-or-later, strong copyleft
- Runtime declaration: Python 3.11+, SQLite, Tesseract OCR, PyMuPDF, optional llama.cpp CPU inference with a local GGUF model
- Offline guarantee: no cloud APIs, no internet-dependent AI services, no GPU/CUDA requirement

## What It Does

Offline Smart Study Assistant accepts PDF, TXT, PNG, and JPG study material, extracts text locally, cleans it, turns it into structured study resources, saves everything in SQLite, and lets students search older uploads offline.

Generated study resources include:

- short, medium, and detailed summaries
- key points and keywords
- question-answer flashcards
- at least 10 MCQs with four options and one correct answer
- short-answer exam questions
- difficulty level and estimated study time
- quiz score tracking and bookmarks
- progress dashboard for quiz attempts and scores

If a local GGUF model is configured, the app uses `llama-cpp-python` with `n_gpu_layers=0`. If no model is available, the app uses deterministic local extractive generators so the MVP still works fully offline for demo and testing.

## Project Structure

```text
offline-smart-study-assistant/
|-- app.py
|-- database.py
|-- models/
|-- services/
|   |-- pdf_reader.py
|   |-- ocr.py
|   |-- llm.py
|   |-- summarizer.py
|   |-- flashcards.py
|   |-- mcq_generator.py
|   |-- keyword_extractor.py
|   |-- cache.py
|   |-- export.py
|   `-- text_processing.py
|-- data/
|-- uploads/
|-- database/
|-- sample_data/
|-- specs/
|-- docs/
|-- requirements.txt
|-- requirements-llm.txt
|-- LICENSE
`-- README.md
```

## Quick Start

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Linux and macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit URL, usually `http://localhost:8501`.

## Optional Local LLM Setup

The MVP works without a model, but the intended CPU SLM path is:

1. Install the llama.cpp Python binding:

```bash
pip install -r requirements-llm.txt
```

2. Put a quantized GGUF model in `models/`, for example:

```text
models/tinyllama.gguf
```

3. Put the model at `models/tinyllama.gguf`, or update `model_path` in `app.py` before starting the app. The app forces CPU mode by using `n_gpu_layers=0`.

Suggested models:

- TinyLlama 1.1B Chat GGUF
- Phi-3 Mini GGUF if the laptop has enough RAM

Do not commit large model files to Git.

## OCR Setup

Image input uses Tesseract locally through `pytesseract`.

Windows:

- Install Tesseract OCR.
- If it is not in `PATH`, update the local `tesseract_cmd` runtime value before processing images.

Linux:

```bash
sudo apt install tesseract-ocr
```

macOS:

```bash
brew install tesseract
```

PDF and TXT uploads do not require Tesseract.

## Offline Demo Script

1. Install dependencies while internet is available.
2. Turn Wi-Fi off.
3. Run `streamlit run app.py`.
4. Go to **Upload Notes**.
5. Upload `sample_data/os_deadlock_notes.txt`.
6. Show the generated summary, flashcards, MCQs, dashboard history, progress page, and search.
7. Search for `deadlock` in **Search Notes**.
8. Re-upload the same file to show cached results.

## SQLite Storage

The app creates `database/study_assistant.sqlite3` automatically with:

- `Documents`
- `StudyContent`
- `StudyProgress`

Uploads are stored in `uploads/`. Generated content is cached by SHA-256 hash of cleaned text.

## Planning Artifacts

- [Spec](specs/001-offline-smart-study-assistant/spec.md)
- [Implementation Plan](specs/001-offline-smart-study-assistant/plan.md)
- [Task Breakdown](specs/001-offline-smart-study-assistant/tasks.md)
- [Data Model](specs/001-offline-smart-study-assistant/data-model.md)
- [JSON Contract](specs/001-offline-smart-study-assistant/contracts/study_content.schema.json)
- [Issue Plan](docs/issues.md)
- [Work Division](docs/work-division.md)

## Repo Audit

Phase 3 audit artifacts:

- `CONTRIBUTING.md`
- `CHANGELOG.md`
- `.pre-commit-config.yaml`
- `.gitlab-ci.yml`
- `pyproject.toml`
- `tests/`

The audit pipeline contains real checks for formatting, linting, type checking, unit tests, dependency audit, security scan, secret scan, YAML validation, license metadata, no-cloud API usage, and Streamlit import smoke testing.

## License

AGPL-3.0-or-later. See [LICENSE](LICENSE).
