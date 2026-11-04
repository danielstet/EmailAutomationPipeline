# CLAUDE.md

## Goal
An AI automation system that takes over repetitive email work for a **fake
company**. It filters spam, classifies each email and routes it to the right
department, replies to or investigates what it can, and escalates the rest to
a human. Target audience: start-ups and small companies that want to cut
employee time spent on routine work. Team: Daniel Stetsyuk, Or Matsliah (both
CS, both do all roles; work is split by timeline: data → automation → UI last).

## Stack
- **LangGraph** (flow and routing between nodes) + **LangChain** (model calls)
- **Ollama** local models only, swappable and compared against each other
- **LangSmith / Langfuse** for tracing every run
- **docker-mailserver** (Postfix + Dovecot) as the fake company's mail server; Roundcube for viewing mailboxes
- **Streamlit** (`app.py`) for the dashboard (a placeholder for now)

## Data
Unstructured email, not a fixed table. Each message is parsed into `from`,
`to`, `date`, `subject`, `body`, `attachments`, `headers`. Empty subjects,
HTML-only bodies and attachment-only mail are expected. Test mail comes from
Kaggle datasets plus synthetic emails, sent into the mail server
(`data/README.md`).

## What the model predicts
For each email: **spam / not spam**, **department** (`billing`, `sales`,
`support`, `hr`, `marketing`, `unclear`), and **action** (auto-reply,
forward, escalate).

## File structure
- `README.md`: M1 project definition (keep it short; details go in `docs/`)
- `app.py`: Streamlit app; `requirements.txt` has pinned versions
- `data/`: data notes plus small samples; large downloads are gitignored
- `mailserver/`: docker compose setup for the mail server; 6 test accounts (`inbox@`, `billing@`, `sales@`, `support@`, `hr@`, `marketing@` on `localmail.test`)
- `docs/` + `mkdocs.yml`: MkDocs documentation site (mail server, pipeline architecture)

## Conventions
- Keep secrets (API keys, `.env`) out of git.
- Local network only: nothing here is hardened for the public internet.
