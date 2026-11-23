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
- **Streamlit** (`app.py`): M2 EDA dashboard on `data/emails_clean.csv` (insight, metrics incl. baselines, 2 charts, sidebar filters, sample table)

## Data
Unstructured email, not a fixed table. Each message is parsed into `from`,
`to`, `date`, `subject`, `body`, `attachments`, `headers`. Empty subjects,
HTML-only bodies and attachment-only mail are expected. Test mail comes from
Kaggle datasets plus synthetic emails, sent into the mail server
(`data/README.md`).

- `scripts/build_dataset.py` builds `data/emails_clean.csv` (committed) and
  `data/department_histogram.png` from the raw Kaggle files (gitignored).
- Department labels come only from the English multi-lang IT tickets (queue →
  department mapping lives in the script). The spam dataset gives only the
  spam label. The customer-support-tickets dataset has random labels, so its
  text is used unlabelled.
- Never commit real people's data: the two HR files (real addresses/LinkedIn)
  stay local. `from` in the committed dataset is one shared made-up pool
  (`customerNNNN@customer.test`, fixed seed), the same for every source so it
  can't leak labels, and never `inbox@` (auto-replies would loop). No `to`
  column: always `inbox@localmail.test`.
- Rows are shuffled with a fixed seed, so order and `id` don't reveal the
  source; rebuilding gives a byte-identical CSV.
- Known gaps: no marketing emails yet (synthetic later), `support` is 78% of
  labelled rows.

## What we learned about the data
- **Imbalance:** `support` is 78.5% of labelled rows; always predicting it
  gives 78.5% accuracy (the M3 department baseline). Spam baseline (always
  "not spam") is 88.5%. Report per-department accuracy / macro-F1, not just
  overall accuracy.
- **The spam data is too easy and artificial:** its text is random filler
  words, and in this dataset an exclamation mark in the subject appears only
  in spam (74% of spam, 0% of other mail). That's an artifact of the synthetic
  source, not a real rule: don't build features or prompts around it, and
  don't trust spam accuracy on this data as a real-world estimate.
- **Spam is shorter:** median body 131 chars vs. 287 for real mail.
- **~1 in 6 business emails has no subject** (16–21% per department), so
  routing must read the body.
- **Labels are noisy:** spot checks found integration questions labelled
  `billing`. Review a sample before trusting them fully.
- Licenses: CC BY 4.0 (IT tickets), CC BY-SA 4.0 (spam: keep share-alike),
  CC0 (support tickets).

## What the model predicts
For each email: **spam / not spam**, **department** (`billing`, `sales`,
`support`, `hr`, `marketing`, `unclear`), and **action** (auto-reply,
forward, escalate).

## File structure
- `README.md`: M1 project definition (keep it short; details go in `docs/`)
- `app.py`: Streamlit app; `requirements.txt` has pinned versions
- `data/`: data notes, the cleaned dataset and its histogram, small samples; raw Kaggle downloads are gitignored
- `scripts/`: data preparation (`build_dataset.py`)
- `mailserver/`: docker compose setup for the mail server; 6 test accounts (`inbox@`, `billing@`, `sales@`, `support@`, `hr@`, `marketing@` on `localmail.test`)
- `docs/` + `mkdocs.yml`: MkDocs documentation site (mail server, pipeline architecture)

## Conventions
- Keep secrets (API keys, `.env`) out of git.
- Local network only: nothing here is hardened for the public internet.
