# Work Division Plan

## Team Roles

| Role | Owner | Responsibilities |
| --- | --- | --- |
| Product + Demo Lead | Nivedhitha | Problem framing, README, demo script, judge-facing explanation. |
| Backend Lead | Backend | SQLite schema, ingestion, caching, search, exports. |
| AI Runtime Lead | AI | llama.cpp setup, GGUF model path, prompt/schema contract, CPU performance. |
| Frontend Lead | Frontend | Streamlit navigation, dashboard, upload flow, quiz mode, progress, and search. |
| DevOps/Audit Lead | DevOps | License, contributing docs, changelog, pre-commit, GitLab CI, local runner checks. |

## Phase 1, Before 10:00 AM

- Product + Demo Lead owns README and problem statement.
- Backend Lead validates schema and folder structure.
- AI Runtime Lead declares model/runtime and offline constraints.
- DevOps/Audit Lead verifies strong copyleft license and issue plan.

## Phase 2, Before Lunch Break

- Backend Lead completes TXT/PDF/image ingestion and SQLite writes.
- AI Runtime Lead connects local GGUF inference and deterministic fallback for development.
- Frontend Lead completes Streamlit upload, dashboard, summaries, flashcards, MCQs, progress, and search.
- Product + Demo Lead records offline demo steps using sample notes.

## Phase 3, Before 3:00 PM

- DevOps/Audit Lead adds at least 10 real checks in pre-commit/GitLab CI.
- Backend and Frontend Leads fix lint/type/test failures.
- Product + Demo Lead updates changelog, contributing guide, and final README screenshots.

## Communication Rules

- Every issue gets an assignee, estimate, and due time.
- Every merge request uses semantic commit style.
- No fake CI jobs. A check must inspect, lint, type-check, test, or scan a real artifact.
- Any feature that needs the internet during demo is out of scope.
