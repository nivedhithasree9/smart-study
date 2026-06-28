from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

import database as db
from services.cache import get_cache_key
from services.export import flashcards_to_csv, summary_to_text
from services.extractor import SUPPORTED_EXTENSIONS, extract_text
from services.llm import generate_study_content
from services.text_processing import clean_text

UPLOAD_DIR = Path("uploads")
MODEL_DIR = Path("models")
DEFAULT_MODEL_PATH = "models/tinyllama.gguf"
CONTEXT_WINDOWS = [1024, 2048, 4096]


st.set_page_config(page_title="Offline Smart Study Assistant", page_icon="OSSA", layout="wide")
db.init_db()
UPLOAD_DIR.mkdir(exist_ok=True)


def init_state() -> None:
    st.session_state.setdefault("model_path", DEFAULT_MODEL_PATH)
    st.session_state.setdefault("threads", default_threads())
    st.session_state.setdefault("context_window", 2048)
    st.session_state.setdefault("tesseract_cmd", "")
    st.session_state.setdefault("selected_document_id", None)
    normalize_settings()


def default_threads() -> int:
    cpu_count = os.cpu_count() or 4
    return min(max(1, cpu_count - 1), cpu_count)


def normalize_settings() -> None:
    if not str(st.session_state.get("model_path", "")).strip():
        st.session_state.model_path = DEFAULT_MODEL_PATH
    cpu_count = max(1, os.cpu_count() or 4)
    try:
        st.session_state.threads = int(st.session_state.get("threads", default_threads()))
    except (TypeError, ValueError):
        st.session_state.threads = default_threads()
    st.session_state.threads = min(max(1, st.session_state.threads), cpu_count)
    if st.session_state.get("context_window") not in CONTEXT_WINDOWS:
        st.session_state.context_window = 2048


def discover_models() -> list[str]:
    MODEL_DIR.mkdir(exist_ok=True)
    return [str(path) for path in sorted(MODEL_DIR.glob("*.gguf"))]


def reset_runtime_defaults() -> None:
    st.session_state.model_path = discover_models()[0] if discover_models() else DEFAULT_MODEL_PATH
    st.session_state.threads = default_threads()
    st.session_state.context_window = 2048
    st.session_state.tesseract_cmd = ""


def save_upload(uploaded_file) -> Path:
    target = UPLOAD_DIR / uploaded_file.name
    suffix = target.suffix
    stem = target.stem
    counter = 1
    while target.exists():
        target = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
        counter += 1
    target.write_bytes(uploaded_file.getbuffer())
    return target


def load_content(document_id: int | None) -> dict | None:
    return db.get_content_for_document(document_id) if document_id else None


def document_picker(label: str = "Choose document") -> int | None:
    documents = db.list_documents()
    if not documents:
        st.info("Upload notes first to unlock this page.")
        return None
    options = {f"#{row['id']} - {row['filename']}": row["id"] for row in documents}
    selected = st.selectbox(label, list(options.keys()))
    return options[selected]


def render_content_overview(content: dict) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Difficulty", content["difficulty"])
    c2.metric("Study Time", content["estimated_study_time"])
    c3.metric("Keywords", len(content["keywords"]))
    c4.metric("MCQs", len(content["mcqs"]))
    st.subheader(content["title"])
    st.caption(f"{content['subject']} | {content['chapter']}")


def page_dashboard() -> None:
    st.title("Dashboard")
    documents = db.list_documents()
    c1, c2, c3 = st.columns(3)
    c1.metric("Documents", len(documents))
    c2.metric("Bookmarked", sum(row["bookmarked"] for row in documents))
    c3.metric("Offline Runtime", "CPU only")
    st.progress(min(1.0, len(documents) / 10), text="MVP demo readiness")
    st.subheader("Recent documents")
    if documents:
        st.dataframe(
            [
                {
                    "File": row["filename"],
                    "Uploaded": row["upload_date"],
                    "Subject": row["subject"] or "-",
                    "Difficulty": row["difficulty"] or "-",
                    "Study Time": row["estimated_study_time"] or "-",
                    "Bookmarked": "Yes" if row["bookmarked"] else "No",
                }
                for row in documents
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No study sessions yet. Upload a TXT, PDF, PNG, or JPG note to begin.")


def page_upload() -> None:
    st.title("Upload Notes")
    uploaded_file = st.file_uploader("Upload PDF, TXT, PNG, or JPG", type=[ext[1:] for ext in SUPPORTED_EXTENSIONS])
    if not uploaded_file:
        st.info("Tip: try sample_data/os_deadlock_notes.txt for the lunch demo.")
        return

    if st.button("Process offline", type="primary", use_container_width=True):
        progress = st.progress(0, text="Saving upload")
        try:
            path = save_upload(uploaded_file)
            progress.progress(20, text="Extracting text locally")
            raw_text = extract_text(path, st.session_state.tesseract_cmd or None)
            extracted = clean_text(raw_text)
            if len(extracted) < 20:
                raise ValueError("Not enough readable text was extracted.")

            progress.progress(40, text="Checking SQLite cache")
            hash_value = get_cache_key(extracted)
            existing = db.get_document_by_hash(hash_value)
            if existing:
                st.session_state.selected_document_id = existing["id"]
                progress.progress(100, text="Loaded cached study content")
                st.success("This document was already processed. Cached results loaded.")
                return

            document_id = db.insert_document(uploaded_file.name, extracted, hash_value)
            progress.progress(65, text="Generating structured study JSON on CPU")
            content = generate_study_content(
                extracted,
                uploaded_file.name,
                st.session_state.model_path,
                st.session_state.threads,
                st.session_state.context_window,
            )
            progress.progress(85, text="Saving summaries, flashcards, and MCQs")
            db.insert_study_content(document_id, content)
            st.session_state.selected_document_id = document_id
            progress.progress(100, text="Done")
            st.success("Study resources generated and saved offline.")
            render_content_overview(content)
            st.write(content["summary_short"])
        except Exception as exc:
            st.error(str(exc))


def page_summary() -> None:
    st.title("AI Summary")
    document_id = st.session_state.selected_document_id or document_picker()
    content = load_content(document_id)
    if not content:
        return
    render_content_overview(content)
    tabs = st.tabs(["Short", "Medium", "Detailed", "Key Points", "Keywords"])
    tabs[0].markdown(content["summary_short"])
    tabs[1].markdown(content["summary_medium"])
    tabs[2].markdown(content["summary_detailed"])
    tabs[3].markdown("\n".join(f"- {clean_text(point)}" for point in content["key_points"]))
    tabs[4].write(", ".join(content["keywords"]))
    st.download_button("Export summary as text", summary_to_text(content), file_name="summary.txt")


def page_flashcards() -> None:
    st.title("Flashcards")
    content = load_content(st.session_state.selected_document_id or document_picker())
    if not content:
        return
    for index, card in enumerate(content["flashcards"], start=1):
        with st.expander(f"Card {index}: {card['question']}"):
            st.write(card["answer"])
    st.download_button("Export flashcards CSV", flashcards_to_csv(content["flashcards"]), "flashcards.csv", "text/csv")


def page_mcq() -> None:
    st.title("MCQ Generator")
    document_id = st.session_state.selected_document_id or document_picker()
    content = load_content(document_id)
    if not content:
        return
    score = 0
    attempted = 0
    with st.form("quiz_form"):
        answers = []
        for index, mcq in enumerate(content["mcqs"], start=1):
            answers.append(
                st.radio(
                    f"{index}. {mcq['question']}",
                    mcq["options"],
                    index=None,
                    key=f"mcq_{document_id}_{index}",
                )
            )
        submitted = st.form_submit_button("Check answers")
    if submitted:
        for answer, mcq in zip(answers, content["mcqs"]):
            if answer is None:
                continue
            attempted += 1
            score += int(answer == mcq["correct_answer"])
        total = len(content["mcqs"])
        percent = round((score / max(1, total)) * 100)
        db.save_progress(document_id, attempted, percent)
        if attempted < total:
            st.warning(f"Answered {attempted}/{total}. Unanswered questions count as wrong.")
        st.success(f"Score: {score}/{total} ({percent}%)")
        with st.expander("Answer key", expanded=True):
            for index, (answer, mcq) in enumerate(zip(answers, content["mcqs"]), start=1):
                if answer == mcq["correct_answer"]:
                    st.success(f"{index}. Correct: {mcq['correct_answer']}")
                else:
                    chosen = answer or "Not answered"
                    st.error(f"{index}. Your answer: {chosen} | Correct: {mcq['correct_answer']}")


def page_history() -> None:
    st.title("Study History")
    documents = db.list_documents()
    for row in documents:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            left.subheader(row["filename"])
            left.caption(f"{row['upload_date']} | {row['difficulty'] or 'Pending'}")
            bookmarked = right.checkbox("Bookmark", value=bool(row["bookmarked"]), key=f"bookmark_{row['id']}")
            db.toggle_bookmark(row["id"], bookmarked)
            if left.button("Open", key=f"open_{row['id']}"):
                st.session_state.selected_document_id = row["id"]
                st.success("Document selected. Open AI Summary, Flashcards, or MCQ Generator.")
    progress = db.list_progress()
    if progress:
        st.subheader("Quiz progress")
        st.dataframe([dict(row) for row in progress], use_container_width=True, hide_index=True)


def page_search() -> None:
    st.title("Search Notes")
    query = st.text_input("Search previous uploads")
    if not query:
        return
    results = db.search_documents(query)
    st.caption(f"{len(results)} result(s)")
    for row in results:
        with st.container(border=True):
            st.subheader(row["title"] or row["filename"])
            st.caption(row["filename"])
            st.write(row["summary_short"] or row["extracted_text"][:300])
            if st.button("Select", key=f"select_{row['id']}"):
                st.session_state.selected_document_id = row["id"]


def page_settings() -> None:
    st.title("Settings")
    normalize_settings()

    st.subheader("Offline AI Runtime")
    available_models = discover_models()
    if available_models:
        model_options = available_models + ["Custom path"]
        current_model = st.session_state.model_path
        selected_model = current_model if current_model in available_models else "Custom path"
        selected_model = st.selectbox("Detected GGUF models", model_options, index=model_options.index(selected_model))
        if selected_model != "Custom path":
            st.session_state.model_path = selected_model
    else:
        st.caption("No `.gguf` model found in `models/`. The app will still work offline using deterministic study generation.")

    st.text_input(
        "GGUF model path",
        key="model_path",
        placeholder=DEFAULT_MODEL_PATH,
        help="Place TinyLlama or Phi-3 Mini GGUF inside the models folder, then set the path here.",
    )

    cpu_count = max(1, os.cpu_count() or 4)
    st.slider(
        "CPU threads",
        min_value=1,
        max_value=cpu_count,
        key="threads",
        help="Use fewer threads if your laptop becomes slow during inference.",
    )
    st.select_slider(
        "Context window",
        options=CONTEXT_WINDOWS,
        key="context_window",
        help="Higher values read more text at once but use more memory.",
    )
    st.text_input(
        "Tesseract executable path (optional)",
        key="tesseract_cmd",
        placeholder=r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    )

    left, right = st.columns([1, 3])
    if left.button("Reset defaults", use_container_width=True):
        reset_runtime_defaults()
        st.rerun()
    right.caption("Defaults are safe for CPU-only demo. A model is optional for fallback mode.")

    model_path = Path(st.session_state.model_path)
    if model_path.exists():
        st.success(f"Model found: `{model_path}`. llama.cpp CPU inference will be used.")
    else:
        st.info(
            "Model not found. Running in offline deterministic fallback mode, so upload, summary, flashcards, MCQs, "
            "search, and SQLite storage still work without internet."
        )

    st.warning("No cloud APIs are used. Keep Wi-Fi off during the demo to prove offline operation.")


def main() -> None:
    init_state()
    st.sidebar.title("Offline Smart Study")
    pages = {
        "Dashboard": page_dashboard,
        "Upload Notes": page_upload,
        "AI Summary": page_summary,
        "Flashcards": page_flashcards,
        "MCQ Generator": page_mcq,
        "Study History": page_history,
        "Search Notes": page_search,
        "Settings": page_settings,
    }
    choice = st.sidebar.radio("Pages", list(pages))
    st.sidebar.caption("CPU-first | Offline-first | SQLite")
    pages[choice]()


if __name__ == "__main__":
    main()
