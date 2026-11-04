# Email Automation Pipeline

**An AI automation system that does a company's repetitive email work: it filters spam, routes each message to the right department, and answers what it can, all on local Ollama models.**

## Project sentence

**Start-ups and small companies** suffer from **expensive employee time being
spent on small, repetitive jobs like sorting, forwarding and answering email**,
and we'll build **an AI automation system that filters, routes and responds to
company email** using **local AI models (Ollama) orchestrated with LangGraph
and LangChain**.

## Target audience

- **Who pays for it:** founders and managers of start-ups and small companies (roughly 5–50 employees). People are their biggest expense, and they can't afford staff whose day is spent on routine email work.
- **Who uses it every day:** operations, support, sales, billing, HR and marketing employees who currently triage a shared inbox by hand. The system takes routine email off their plate and leaves them the complex cases.
- **Why local models fit them:** these companies want automation without sending sensitive business email to external AI services or paying per-request API costs.

## The problem

In production environments, many small, repetitive jobs need either constant human attention or rigid deterministic code.
People are the most expensive line item in a start-up, and a large share of their time goes to this routine work instead of the complex work only they can do.
Hand-written rules break as soon as the input varies, and hiring more people doesn't scale.
AI models can handle the variability, and running them locally (Ollama) keeps company data in-house and inference costs near zero.
We start with email: it's high-volume, noisy and repetitive, and it touches every department.

## What we're building

We're building a **fake company** with its own mail server and departments
(billing, sales, support, HR, marketing). It receives a constant stream of
email, some of it noise and some of it relevant. The automation system:

1. **Filters**: detects spam and noise and moves it to the spam folder.
2. **Classifies and routes**: recognizes what each email is about and forwards it to the right department.
3. **Responds and investigates**: drafts or sends replies to the emails it can handle, and gathers context on the rest before a human sees them.
4. **Escalates**: flags anything it isn't confident about for human review.

The flow is a LangGraph graph whose nodes call local models through
LangChain. It is model-agnostic, so we can swap in and compare different
models pulled from Ollama. Every run is traced in LangSmith / Langfuse for
debugging and evaluation.

## Persona + scenario

**Dana, operations manager at a 20-person start-up.** Every morning the
shared inbox has about 80 new emails. Before the system, two people spent half
their day reading, forwarding and answering routine questions. Now, when Dana
opens the dashboard, spam is already gone and department emails are already in
the right mailboxes. Routine questions ("Where's my invoice?") have been
answered. Dana only reviews the handful of emails the system flagged as
unclear, and both people are free for work that actually needs them.

## Data source

**Our data is email, not a fixed table.** The system's input is real email
arriving at our local mail server (Postfix + Dovecot). The server has a triage
inbox, five department mailboxes and a spam folder. Emails don't share a fixed
row/column format: each one is an unstructured MIME message. The pipeline
parses every message into the same set of fields:

| Field | Notes |
|---|---|
| `from`, `to`, `date` | Always present in the headers |
| `subject` | Can be empty |
| `body` | Plain text, HTML-only, or empty (attachment-only messages) |
| `attachments` | Zero or more, any file type |
| `headers` | Reply chains, mailing-list and auto-generated markers |

Handling messy input (empty subjects, HTML-only bodies, attachment-only mail,
forwarded threads) is part of what the system has to do.

**Where the test email comes from:** we fill the fake company's mailboxes
using public Kaggle datasets, which include spam, customer support tickets,
HR emails, marketing and email tone. We send them into the mail server as real
messages, together with synthetic emails generated for the fake company. The
candidate datasets are listed here (still being checked; unsuitable ones will
be removed):
[Kaggle datasets for mail automation (Google Doc)](https://docs.google.com/document/d/1PUPexD2djFNNJ2YQwhDMbW08m1U5ldpLtCQqNLAMqP4/edit?usp=sharing)

## What the system shows

There's no end-user app. The "screens" are where you watch and verify the system working:
- **Mailboxes (Roundcube webmail):** emails disappear from the triage inbox and appear in the right department mailbox or spam folder, along with any replies that were sent.
- **Traces (LangSmith / Langfuse):** every email's path through the graph, including which node ran, what the model was asked, what it answered, and how long it took.
- **Metrics:** routing accuracy, spam precision, and how many emails were handled with no human involved, compared across Ollama models.

## What the model will predict

For each incoming email (from its sender, subject and body):
- **Spam / not spam**, a binary category
- **Department**: `billing`, `sales`, `support`, `hr`, `marketing`, or `unclear`
- **Action**: auto-reply, forward only, or escalate to a human

## User stories

1. As an **operations manager**, I want spam filtered out and every email routed to the right department automatically, so that nobody has to triage the shared inbox by hand.
2. As a **support employee**, I want routine questions answered by the system, so that I only handle the complex cases.
3. As a **founder**, I want to see how much email work the system handled without humans and how accurate it was, so that I can decide how much of the team's time it can free up.

## Risks

| Risk | Type | What we'll do if it happens |
|---|---|---|
| No public labeled dataset fits our fake company's departments | Data | Generate a synthetic labeled email set with an LLM and hand-check a sample |
| Local Ollama models are too slow or inaccurate on our hardware | Technical | Benchmark several model sizes, use small models for filtering and routing, and add a deterministic fallback for spam |
| Auto-replies and "investigation" are harder to make reliable than routing | Schedule | Ship filtering and routing first; auto-reply becomes a stretch goal behind a human-approval step |

## Team & roles

| Name | Faculty | Role |
|---|---|---|
| Daniel Stetsyuk | Computer Science | All roles: Product, Developer, Data, UX / UI |
| Or Matsliah | Computer Science | All roles: Product, Developer, Data, UX / UI |

We're a team of two, and we don't split the project by role. We both work
on every part and divide the work **by timeline**, finishing each phase
before the next:

1. **Data:** build the fake company's email corpus from Kaggle and synthetic sources, and load it into the mail server.
2. **Automation:** the LangGraph / LangChain pipeline (filter, classify, route, respond), local Ollama models, and LangSmith / Langfuse tracing.
3. **Frontend and UX / UI:** how the system is presented and demoed. This comes last.

## How to run

The mail server is built and running. The pipeline itself is in progress.

```bash
cd mailserver
docker compose up -d
```

The one-time steps (TLS certificate and hosts-file entry) and the test
accounts are covered in the full documentation.

## More information: full documentation

This README covers only the basics. The full documentation lives in the
MkDocs site under [`docs/`](docs/index.md). It covers the mail server setup,
test accounts, the webmail UI and the pipeline architecture. To view it, run
this from the repo root:

```bash
docker run --rm -it -p 8000:8000 -v "${PWD}:/docs" squidfunk/mkdocs-material
```

Then open <http://localhost:8000>.
