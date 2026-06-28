from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

import streamlit as st

import database as db
from services.cache import get_cache_key
from services.export import flashcards_to_csv, summary_to_text
from services.extractor import SUPPORTED_EXTENSIONS, extract_text
from services.flashcards import generate_flashcards
from services.llm import generate_study_content
from services.mcq_generator import generate_mcqs
from services.text_processing import clean_text

UPLOAD_DIR = Path("uploads")
DEFAULT_MODEL_PATH = "models/tinyllama.gguf"
CONTEXT_WINDOWS = [1024, 2048, 4096]
APP_DEPLOY_VERSION = "2026.06.28-flashcards-hotfix"


st.set_page_config(page_title="Offline Smart Study Assistant", page_icon="OSSA", layout="wide")
db.init_db()
UPLOAD_DIR.mkdir(exist_ok=True)


def init_state() -> None:
    st.session_state.setdefault("device_id", current_device_id())
    st.session_state.setdefault("model_path", DEFAULT_MODEL_PATH)
    st.session_state.setdefault("threads", default_threads())
    st.session_state.setdefault("context_window", 2048)
    st.session_state.setdefault("tesseract_cmd", "")
    st.session_state.setdefault("selected_document_id", None)
    normalize_settings()


def current_device_id() -> str:
    query_device = str(st.query_params.get("device", "")).strip()
    if query_device:
        return query_device
    device_id = uuid.uuid4().hex
    st.query_params["device"] = device_id
    return device_id


def owner_id() -> str:
    return st.session_state["device_id"]


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
    return db.get_content_for_document(document_id, owner_id()) if document_id else None


def document_picker(label: str = "Choose document") -> int | None:
    documents = db.list_documents(owner_id())
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
    documents = db.list_documents(owner_id())
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
            hash_value = f"{owner_id()}:{get_cache_key(extracted)}"
            existing = db.get_document_by_hash(hash_value, owner_id())
            if existing:
                st.session_state.selected_document_id = existing["id"]
                progress.progress(100, text="Loaded cached study content")
                st.success("This document was already processed. Cached results loaded.")
                return

            document_id = db.insert_document(uploaded_file.name, extracted, hash_value, owner_id())
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
    document_id = st.session_state.selected_document_id or document_picker()
    content = load_content(document_id)
    if not content:
        return
    document = db.get_document(document_id, owner_id())
    flashcards = content.get("flashcards", [])
    if document and len(flashcards) < 20:
        flashcards = generate_flashcards(document["extracted_text"], 20)
        try:
            db.update_flashcards(document_id, flashcards, owner_id())
            st.info("Flashcards were refreshed from the document text.")
        except AttributeError:
            st.info("Flashcards were refreshed for this page. Reboot the app once to save them permanently.")
    st.caption(f"{len(flashcards)} flashcards available for this document.")
    for index, card in enumerate(flashcards, start=1):
        with st.expander(f"Card {index}: {card['question']}"):
            st.write(card["answer"])
    st.download_button("Export flashcards CSV", flashcards_to_csv(flashcards), "flashcards.csv", "text/csv")


def page_mcq() -> None:
    st.title("MCQ Generator")
    st.caption(f"MCQ quiz mode active | deploy {APP_DEPLOY_VERSION}")
    document_id = st.session_state.selected_document_id or document_picker()
    content = load_content(document_id)
    if not content:
        return
    document = db.get_document(document_id, owner_id())
    mcqs = content.get("mcqs", [])
    has_real_mcqs = all(
        isinstance(mcq, dict)
        and isinstance(mcq.get("question"), str)
        and isinstance(mcq.get("options"), list)
        and len(mcq["options"]) == 4
        and mcq.get("correct_answer") in mcq["options"]
        for mcq in mcqs
    )
    if document and (len(mcqs) < 20 or not has_real_mcqs):
        mcqs = generate_mcqs(document["extracted_text"], count=20, variant_seed="mcq-page-repair")
        db.update_mcqs(document_id, mcqs, owner_id())
        st.info("MCQs were refreshed from the document text.")
    left, right = st.columns([3, 1])
    left.caption(f"{len(mcqs)} multiple-choice questions available for this document.")
    if right.button("Regenerate quiz questions", use_container_width=True):
        if not document:
            st.error("Could not find the selected document text.")
            return
        mcqs = generate_mcqs(document["extracted_text"], count=20, variant_seed=time.time_ns())
        db.update_mcqs(document_id, mcqs, owner_id())
        st.success("New quiz questions generated for the same document.")
    score = 0
    attempted = 0
    with st.form("quiz_form"):
        answers = []
        for index, mcq in enumerate(mcqs, start=1):
            options = [str(option) for option in mcq["options"]]
            answers.append(
                st.radio(
                    f"Question {index}: {mcq['question']}",
                    options,
                    index=None,
                    key=f"mcq_{document_id}_{index}",
                )
            )
        submitted = st.form_submit_button("Check answers")
    if submitted:
        for answer, mcq in zip(answers, mcqs):
            if answer is None:
                continue
            attempted += 1
            score += int(answer == mcq["correct_answer"])
        total = len(mcqs)
        percent = round((score / max(1, total)) * 100)
        db.save_progress(document_id, attempted, percent, owner_id())
        if attempted < total:
            st.warning(f"Answered {attempted}/{total}. Unanswered questions count as wrong.")
        st.success(f"Score: {score}/{total} ({percent}%)")
        with st.expander("Answer key", expanded=True):
            for index, (answer, mcq) in enumerate(zip(answers, mcqs), start=1):
                if answer == mcq["correct_answer"]:
                    st.success(f"{index}. Correct: {mcq['correct_answer']}")
                else:
                    chosen = answer or "Not answered"
                    st.error(f"{index}. Your answer: {chosen} | Correct: {mcq['correct_answer']}")


def page_history() -> None:
    st.title("Study History")
    documents = db.list_documents(owner_id())
    for row in documents:
        with st.container(border=True):
            left, right = st.columns([4, 1])
            left.subheader(row["filename"])
            left.caption(f"{row['upload_date']} | {row['difficulty'] or 'Pending'}")
            bookmarked = right.checkbox("Bookmark", value=bool(row["bookmarked"]), key=f"bookmark_{row['id']}")
            db.toggle_bookmark(row["id"], bookmarked, owner_id())
            if left.button("Open", key=f"open_{row['id']}"):
                st.session_state.selected_document_id = row["id"]
                st.success("Document selected. Open AI Summary, Flashcards, or MCQ Generator.")
    progress = db.list_progress(owner_id())
    if progress:
        st.subheader("Quiz progress")
        st.dataframe([dict(row) for row in progress], use_container_width=True, hide_index=True)


def page_progress() -> None:
    st.title("Progress")
    documents = db.list_documents(owner_id())
    progress = db.list_progress(owner_id())

    total_attempts = len(progress)
    total_mcqs = sum(row["completed_mcqs"] for row in progress)
    scores = [row["last_score"] for row in progress]
    average_score = round(sum(scores) / len(scores)) if scores else 0
    best_score = max(scores) if scores else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Study Sessions", len(documents))
    c2.metric("Quiz Attempts", total_attempts)
    c3.metric("MCQs Attempted", total_mcqs)
    c4.metric("Best Score", f"{best_score}%")

    st.progress(average_score / 100 if scores else 0, text=f"Average quiz score: {average_score}%")

    if not progress:
        st.info("Complete an MCQ quiz to start tracking progress.")
        return

    st.subheader("Recent Quiz Activity")
    st.dataframe(
        [
            {
                "Document": row["filename"],
                "Attempted MCQs": row["completed_mcqs"],
                "Score": f"{row['last_score']}%",
                "Updated": row["updated_at"],
            }
            for row in progress
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Document Completion")
    for row in documents:
        document_attempts = [item for item in progress if item["filename"] == row["filename"]]
        best_document_score = max((item["last_score"] for item in document_attempts), default=0)
        with st.container(border=True):
            left, right = st.columns([3, 1])
            left.write(row["filename"])
            left.progress(best_document_score / 100, text=f"Best quiz score: {best_document_score}%")
            right.metric("Attempts", len(document_attempts))


def page_search() -> None:
    st.title("Search Notes")
    query = st.text_input("Search previous uploads")
    if not query:
        return
    results = db.search_documents(query, owner_id())
    st.caption(f"{len(results)} result(s)")
    for row in results:
        with st.container(border=True):
            st.subheader(row["title"] or row["filename"])
            st.caption(row["filename"])
            st.write(row["summary_short"] or row["extracted_text"][:300])
            if st.button("Select", key=f"select_{row['id']}"):
                st.session_state.selected_document_id = row["id"]


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
        "Progress": page_progress,
        "Search Notes": page_search,
    }
    choice = st.sidebar.radio("Pages", list(pages), key=f"active_page_{APP_DEPLOY_VERSION}")
    st.sidebar.caption(f"Private device: {owner_id()[:8]} | CPU-first | Offline-first | {APP_DEPLOY_VERSION}")
    pages[choice]()


if __name__ == "__main__":
    main()
