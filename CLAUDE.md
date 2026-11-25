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
- **Jupyter** (`eda.ipynb`): the M2 deliverable, an EDA notebook on `data/emails_clean.csv` (four questions: column types, quality, distributions, correlation/leakage; a conclusion cell under every chart; insight + baselines at the top). Must pass Restart & Run All.
- **Streamlit** (`app.py`): the earlier M2 dashboard, no longer required (course update 24/11); it returns once there's a model to show

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
- **Spam is shorter:** median body 131 chars vs. 285 for real mail.
- **~1 in 6 business emails has no subject** (16–21% per department), so
  routing must read the body.
- **Labels are noisy:** spot checks found integration questions labelled
  `billing`. Review a sample before trusting them fully.
- **Labels look generated from the text (or vice versa):** "billing",
  "payment", "invoice", "subscription" appear in 0% of the 13,923 non-billing
  emails. Billing routing will look easier here than on real mail; `sales` and
  `unclear` have no marker words and are the hard classes.
- **Leaks (never model inputs):** `source` and `reply` decide whether a row can
  be spam / has a department; `id` and `from` are identifiers. Empty subjects
  exist only in IT tickets, so "no subject" means "not spam" in this data only.
  Model inputs are `subject` + `body` only.
- **Surface features don't route:** length, digits and has-subject have
  association < 0.1 with department; the signal is in the words.
- **366 support-ticket bodies (1.1%) have cut-off generator fragments**
  (`{product_p`, pasted code/JSON). Kept and flagged (unlabelled source); the
  raw files aren't needed to see them, but fixing them in `build_dataset.py`
  needs the raw Kaggle CSV.
- Main metrics for M3: department → macro-F1 (baseline 0.18), spam → precision, beat 27.9% (rule "body under 200 chars = spam", catches 99.5% of spam; "always not spam" flags nothing so its precision is meaningless), accuracy above 88.5%.
- Full EDA conclusions: `docs/data/eda-conclusions.md` (keep in sync with the notebook).
- Licenses: CC BY 4.0 (IT tickets), CC BY-SA 4.0 (spam: keep share-alike),
  CC0 (support tickets).

## What the model predicts
For each email: **spam / not spam**, **department** (`billing`, `sales`,
`support`, `hr`, `marketing`, `unclear`), and **action** (auto-reply,
forward, escalate).

## File structure
- `README.md`: M1 project definition (keep it short; details go in `docs/`)
- `eda.ipynb`: M2 EDA notebook (run from the repo root)
- `app.py`: Streamlit dashboard (not part of M2 anymore); `requirements.txt` has pinned versions
- `data/`: data notes, the cleaned dataset and its histogram, small samples; raw Kaggle downloads are gitignored
- `scripts/`: data preparation (`build_dataset.py`)
- `mailserver/`: docker compose setup for the mail server; 6 test accounts (`inbox@`, `billing@`, `sales@`, `support@`, `hr@`, `marketing@` on `localmail.test`)
- `docs/` + `mkdocs.yml`: MkDocs documentation site (mail server, pipeline architecture)

## Conventions
- Keep secrets (API keys, `.env`) out of git.
- Local network only: nothing here is hardened for the public internet.
