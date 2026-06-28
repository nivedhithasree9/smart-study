# Contributing

Thank you for improving Offline Smart Study Assistant.

## Development Rules

- Keep the core app offline-first. Do not add cloud AI APIs or internet-dependent processing.
- Keep inference CPU-first. Do not require CUDA, GPU-only libraries, or hosted model services.
- Use semantic commits, for example `feat: add quiz progress` or `fix: clean pdf text`.
- Keep generated data out of Git. Do not commit SQLite databases, uploaded files, model weights, or caches.
- Run checks before pushing.

## Local Setup

```bash
python -m venv .venv
pip install -r requirements.txt
pip install -r requirements-dev.txt
pre-commit install
```

Optional local LLM support:

```bash
pip install -r requirements-llm.txt
```

## Checks

```bash
pre-commit run --all-files
pytest
python -m py_compile app.py database.py services/*.py
```

## Offline Demo Discipline

The demo must work with Wi-Fi off after dependencies and optional local models are already installed. The app may read files from local folders, run Tesseract, use SQLite, and run llama.cpp CPU inference, but it must not call cloud APIs.
