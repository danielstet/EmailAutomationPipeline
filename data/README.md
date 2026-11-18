# Data

Our data is **email**: unstructured messages arriving at the local mail server
(see the root [README](../README.md#data-source)). The pipeline parses each
message into the same fields: `from`, `to`, `date`, `subject`, `body`,
`attachments`, `headers`.

## Files in git

- `emails_clean.csv` is the cleaned, combined dataset (34,801 emails) that
  gets sent into the mail server. Columns:

  | Column | Meaning |
  |---|---|
  | `id` | Row number |
  | `source` | Which raw dataset the row came from |
  | `from`, `to` | Sender (synthetic) and recipient (always `inbox@localmail.test`) |
  | `subject`, `body` | Email text. The subject can be empty, as in real email |
  | `spam` | 1 = spam, 0 = not spam |
  | `department` | `billing`, `sales`, `support`, `hr`, `marketing`, `unclear`, or empty when the source has no reliable label |
  | `reply` | A reference reply written by a support agent (multi-lang tickets only) |

- `department_histogram.png` shows the distribution of the target variable.
- `sample_emails.csv` is a small hand-written sample used by `app.py` for a preview.

## Raw sources (not in git)

Download these from Kaggle into this folder, then rebuild with
`python scripts/build_dataset.py` from the repo root.

| File | Kaggle dataset | Used for |
|---|---|---|
| `aa_dataset-tickets-multi-lang-5-2-50-version.csv` | [Customer IT Support - Ticket Dataset](https://www.kaggle.com/datasets/tobiasbueck/multilingual-customer-support-tickets) | Department labels + reference replies |
| `spam_email_dataset.csv` | [Spam Email Detection Dataset (Clean & ML Ready)](https://www.kaggle.com/datasets/ssssws/spam-email-detection-dataset-clean-and-ml-ready) | Spam / not-spam label |
| `customer_support_tickets.csv` | [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) | Unlabelled incoming mail (text only) |
| `HREmailData.csv` | [Human Resource Jobs Emails](https://www.kaggle.com/datasets/mohamedramadan2040/hr-jobs-emails) | Kept locally only (real addresses, see below) |
| `HR Curated List BM.csv` | [150+ HR Email Addresses for Jobs](https://www.kaggle.com/datasets/peshimaammuzammil/150-hr-email-addresses) | Kept locally only (real names and LinkedIn URLs) |

The two HR files contain addresses, names and LinkedIn URLs of real people and
no email text, so they are never copied into `emails_clean.csv` or committed.
Synthetic emails for the fake company (for example marketing mail) will be
added later.
