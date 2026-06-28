# Phase 1 Issue Plan

All due dates are June 28, 2026, Asia/Kolkata time. Assignees can be mapped to GitLab users when the team finalizes handles.

| ID | Title | Assignee | Estimate | Due | Priority | Acceptance Criteria |
| --- | --- | --- | --- | --- | --- | --- |
| OSSA-001 | Finalize Phase 1 README and problem statement | Nivedhitha | 30 min | 2026-06-28 10:00 | P0 | README declares idea, offline guarantee, model/runtime, license, and demo plan. |
| OSSA-002 | Write Spec Kit documents | Nivedhitha | 45 min | 2026-06-28 10:00 | P0 | Spec, plan, tasks, data model, and JSON contract exist under `specs/`. |
| OSSA-003 | Define SQLite schema | Backend | 40 min | 2026-06-28 11:00 | P0 | Documents, StudyContent, and StudyProgress schema support MVP queries. |
| OSSA-004 | Implement document ingestion | Backend | 1 hr | 2026-06-28 12:00 | P0 | TXT and PDF extraction work; invalid files show useful errors. |
| OSSA-005 | Add Tesseract OCR path | Backend | 1 hr | 2026-06-28 12:30 | P1 | PNG/JPG text extraction works when Tesseract is installed. |
| OSSA-006 | Add llama.cpp CPU inference service | AI | 1.5 hr | 2026-06-28 13:00 | P0 | Local GGUF path is configurable; no cloud API calls exist. |
| OSSA-007 | Build Streamlit upload and dashboard pages | Frontend | 1.5 hr | 2026-06-28 13:00 | P0 | User can upload, process, and view generated content. |
| OSSA-008 | Implement offline search and cache | Backend | 1 hr | 2026-06-28 13:30 | P0 | Same content hash reuses previous outputs; search returns prior notes. |
| OSSA-009 | Add quiz/export bonus features | Frontend | 1 hr | 2026-06-28 14:00 | P1 | MCQ quiz mode works; CSV/PDF export works locally. |
| OSSA-010 | Repo audit pipeline with 10 real checks | DevOps | 1 hr | 2026-06-28 15:00 | P0 | CI/pre-commit run real formatting, lint, type, tests, security, and metadata checks. |

## GitLab Issue Labels

- `phase::plan`
- `phase::mvp`
- `phase::audit`
- `priority::p0`
- `priority::p1`
- `area::frontend`
- `area::backend`
- `area::ai`
- `area::devops`

## Milestones

- Phase 1 Plan & Spec: due 2026-06-28 10:00
- Phase 2 MVP Demo: due 2026-06-28 lunch break
- Phase 3 Repo Audit: due 2026-06-28 15:00
