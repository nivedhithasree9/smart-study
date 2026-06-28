# Research Notes

## Why CPU-first

Most student laptops have CPUs, but not dedicated GPUs. A small local model with quantized GGUF weights can run acceptably for summarization and structured extraction when prompts are short and cached.

## Runtime Choice

`llama.cpp` is selected because it supports quantized GGUF models, runs on CPU, has Python bindings, and does not require a server or cloud service.

## Model Candidates

| Model | Reason |
| --- | --- |
| TinyLlama 1.1B Chat GGUF | Small enough for low-memory laptops; good for hackathon demo speed. |
| Phi-3 Mini GGUF | Better reasoning quality; heavier but still CPU-capable with quantization. |

## OCR Choice

Tesseract OCR is selected because it is free, offline, and available on Windows, Linux, and macOS. OCR quality depends on image clarity, so the MVP will show warnings when extracted text is too short.

## Data Privacy

All uploaded files, extracted text, generated summaries, and quiz data stay on the user's machine in local folders and SQLite.
