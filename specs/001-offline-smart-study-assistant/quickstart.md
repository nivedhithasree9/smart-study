# Quickstart For Demo

## Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Install Tesseract OCR from the official Windows installer and add it to PATH.

## Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
sudo apt install tesseract-ocr
streamlit run app.py
```

## macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
brew install tesseract
streamlit run app.py
```

## Model Setup

Place one local GGUF model in `models/`, for example:

- TinyLlama 1.1B Chat GGUF
- Phi-3 Mini GGUF

The app must not download models during the offline demo.
