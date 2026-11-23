# Data Preparation

How the raw Kaggle downloads became `data/emails_clean.csv`, why each change
was made, and what the final dataset looks like. Everything below is done by
`scripts/build_dataset.py` (run `python scripts/build_dataset.py` from the repo
root). For a column-by-column reference, see
[Combined Dataset](combined-dataset.md).

## Starting point: the raw files

| File | Rows × columns | What it really contained |
|---|---|---|
| `aa_dataset-tickets-multi-lang-5-2-50-version.csv` | 28,587 × 16 | Synthetic IT support tickets with subject, body, agent reply and a `queue` label. 43% German. |
| `spam_email_dataset.csv` | 10,000 × 20 | Spam / not-spam emails (60/40) plus 16 pre-computed feature columns. The text is random filler words. |
| `customer_support_tickets.csv` | 8,469 × 17 | Generated support tickets with customer details and a `Ticket Type` label. Every description has template placeholders. |
| `HREmailData.csv` | 78,717 × 1 | Only email addresses, no email text |
| `HR Curated List BM.csv` | 104 × 3 | Names and LinkedIn URLs of real people |
| `customer_support_tickets.csv.zip` | n/a | A zipped copy of the support tickets file |

## What we changed, and why

### Per source

**IT support tickets (multi-lang): 28,587 → 16,338 rows**

| Change | Why |
|---|---|
| Dropped the 12,249 German rows | The fake company and the model prompts are in English. Mixing languages would make the comparison between Ollama models unfair. |
| Mapped the 10 `queue` values to our departments | The pipeline predicts our departments, not the dataset's queues. Technical, Product and IT Support, Service Outages and Customer Service → `support`; Billing and Payments, Returns and Exchanges → `billing`; Sales and Pre-Sales → `sales`; Human Resources → `hr`; General Inquiry → `unclear`. |
| Kept the agent's `answer` as `reply` | It's a reference answer for judging auto-replies later. |
| Turned literal `\n` into real line breaks (740 rows) | The text arrived with escaped newlines, which would show up literally in the emails. |
| Left 2,607 empty subjects empty | Real email has empty subjects, and the pipeline has to handle them. |
| Dropped `type`, `priority`, `language`, `version`, `tag_1`–`tag_8` | They aren't part of an email and aren't predicted. |

**Spam dataset: 10,000 rows, all kept**

| Change | Why |
|---|---|
| Kept only `subject`, `email_text` → `body`, `label` → `spam` | The 16 feature columns (`num_links`, `sender_reputation_score`, `contains_urgency_terms`, …) don't exist in a real incoming email. The pipeline has to work from the email itself. |
| Gave it no department | The dataset has no routing label. |

**Customer support tickets: 8,469 → 8,463 rows**

| Change | Why |
|---|---|
| **Dropped the `Ticket Type` label** | It's random: it doesn't depend on the ticket at all (a "billing inquiry" is as likely to be about a display issue as anything else). Training or scoring on it would mean learning noise. The text is kept as unlabelled incoming mail. |
| **Filled the template placeholders** | Every description had `{product_purchased}`, and about 1,060 also had about 300 other spellings (`{Product_id}`, `{{item.price}}`, `{error_message}`…). Product placeholders → the ticket's product; `{error_message}` → one of six realistic error messages (seeded); other single-name placeholders → removed. 49 code-like fragments (`{ int i; }`) are left in as pasted-code noise. |
| Dropped customer name, age, gender, status, resolution, priority, channel, ratings, times | They aren't part of an email and aren't predicted. |
| 6 rows removed as duplicates | See below. |

**HR files and the zip: not used**

The two HR files contain only real people's addresses, names and LinkedIn
URLs, and no email text. They stay on our machines (gitignored) and nothing
from them is in the dataset. The zip is a duplicate of a file we already have.

### Across the combined dataset

| Change | Why |
|---|---|
| Dropped rows with an empty body, then exact duplicates of (`subject`, `body`) | No empty emails, and no email counted twice. Only 6 duplicates existed. |
| **Replaced every sender with one shared pool** of 1,000 made-up addresses (`customer0000`–`customer0999@customer.test`), assigned at random | The original senders differed by source (`@customer.test`, `@example.com`, random `@gmail.com`), so the sender's domain revealed which dataset, and so which labels, an email came from. Now every address appears in all three sources. The sender also mustn't be `inbox@`, or auto-replies would loop back into the triage inbox. |
| **Dropped the `to` column** | It was always `inbox@localmail.test`. The sending script sets it. |
| **Shuffled the rows**, then assigned `id` | The sources were stacked in blocks (ids 1–16,338 all tickets, then all the spam…), so any slice of the file, like "the first 500 rows", was one source with no spam. |
| Fixed random seed (42) | The sender pool, the error messages and the shuffle are random but reproducible: every rebuild gives a byte-identical CSV. |

## Final dataset

**`data/emails_clean.csv`: 34,801 emails × 8 columns, about 17 MB, committed to git.**

| Source | Rows | `spam` | `department` |
|---|---|---|---|
| `multilang_tickets` | 16,338 | all 0 | labelled |
| `spam_dataset` | 10,000 | 3,995 spam / 6,005 not | empty |
| `support_tickets` | 8,463 | all 0 | empty |
| **Total** | **34,801** | **3,995 spam (11%)** | **16,338 labelled** |

### Column schema

| # | Column | Type | Values | Empty allowed? |
|---|---|---|---|---|
| 1 | `id` | integer | 1–34,801, unique, in shuffled order | No |
| 2 | `source` | string | `multilang_tickets`, `spam_dataset`, `support_tickets` | No |
| 3 | `from` | string | `customer0000@customer.test` … `customer0999@customer.test` | No |
| 4 | `subject` | string | Up to 234 characters, may contain emoji | Yes (2,607 rows) |
| 5 | `body` | string (multi-line) | 6–1,147 characters | No |
| 6 | `spam` | integer | `0` or `1` | No |
| 7 | `department` | string | `billing`, `sales`, `support`, `hr`, `unclear` (`marketing` defined but no rows yet) | Yes: empty = no reliable label |
| 8 | `reply` | string (multi-line) | Agent's reference reply | Yes: only multilang tickets have one |

### Target variable: department

| `billing` | `sales` | `support` | `hr` | `marketing` | `unclear` |
|---|---|---|---|---|---|
| 2,415 | 513 | 12,826 | 348 | 0 | 236 |

The histogram is in `data/department_histogram.png` and in the root README.

## What goes to the model

The model only sees what a real email would contain. Everything else is
ground truth, kept in the CSV and joined back by `id` to score the results.

| Role | Columns | Notes |
|---|---|---|
| **Model input** (sent as the email) | `subject`, `body`, `from` | `from` is random, so it carries no information; it's there because a real email has one. |
| **Target: spam filter** | `spam` | All 34,801 rows. |
| **Target: routing** | `department` | Only the 16,338 labelled rows; rows with an empty department are left out of routing scores. |
| **Reference for auto-replies** | `reply` | Compared with what the system writes; never shown to the model. |
| **Never shown to the model** | `id`, `source` | `id` travels as a hidden `X-Dataset-Id` header only to link results back. `source` would leak the labels. |

The pipeline uses local Ollama models through prompts, so "training" here
means the data the models are evaluated on and, if we add few-shot
examples, the examples taken from it. The third prediction, **action**
(auto-reply / forward / escalate), has no label in the dataset yet.

## Known limitations

- **Synthetic text.** None of it is real company mail. The spam dataset is random filler words, and some support tickets contain nonsense left by the generator.
- **Imbalanced classes.** `support` is 78% of labelled rows; `marketing` has none yet, to be filled with synthetic emails. We'll report per-department accuracy, not only overall accuracy.
- **Some labels look wrong.** Spot checks found integration questions labelled `billing` (for example "Implementing Magento with PyCharm"). The labels need a manual review of a sample.
- **No real HTML emails, attachments or dates.** The sending script sets the date; HTML and attachments will come from synthetic emails.
- **Anonymisation tokens** like `<name>` and `<tel_num>` remain in 607 bodies and 8,010 replies (from the dataset author).
- **No train/test split yet.**
