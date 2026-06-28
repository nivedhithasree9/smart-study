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


st.set_page_config(page_title="Offline Smart Study Assistant", page_icon="OSSA", layout="wide")
db.init_db()
UPLOAD_DIR.mkdir(exist_ok=True)


def init_state() -> None:
    st.session_state.setdefault("model_path", "models/tinyllama.gguf")
    st.session_state.setdefault("threads", max(1, (os.cpu_count() or 4) - 1))
    st.session_state.setdefault("context_window", 2048)
    st.session_state.setdefault("tesseract_cmd", "")
    st.session_state.setdefault("selected_document_id", None)


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
    tabs[0].write(content["summary_short"])
    tabs[1].write(content["summary_medium"])
    tabs[2].write(content["summary_detailed"])
    tabs[3].markdown("\n".join(f"- {point}" for point in content["key_points"]))
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
            answers.append(st.radio(f"{index}. {mcq['question']}", mcq["options"], key=f"mcq_{document_id}_{index}"))
        submitted = st.form_submit_button("Submit quiz")
    if submitted:
        for answer, mcq in zip(answers, content["mcqs"]):
            attempted += 1
            score += int(answer == mcq["correct_answer"])
        percent = round((score / max(1, attempted)) * 100)
        db.save_progress(document_id, attempted, percent)
        st.success(f"Score: {score}/{attempted} ({percent}%)")
    with st.expander("Answer key"):
        for index, mcq in enumerate(content["mcqs"], start=1):
            st.write(f"{index}. {mcq['correct_answer']}")


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
    st.text_input("GGUF model path", key="model_path")
    st.slider("CPU threads", min_value=1, max_value=max(1, os.cpu_count() or 8), key="threads")
    st.select_slider("Context window", options=[1024, 2048, 4096], key="context_window")
    st.text_input("Tesseract executable path (optional)", key="tesseract_cmd")
    model_exists = Path(st.session_state.model_path).exists()
    st.info(f"Model status: {'found, llama.cpp will be used' if model_exists else 'not found, local deterministic fallback active'}")
    st.warning("Core app makes no cloud calls. Keep Wi-Fi off during demo to prove offline operation.")


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
