# Combined Dataset

`data/emails_clean.csv` is the fake company's incoming mail: **34,801 emails,
8 columns**, built by `scripts/build_dataset.py` from three Kaggle datasets
(sources and cleaning steps are in `data/README.md` and the root README).

Each row is one email that will be delivered to `inbox@localmail.test`.
Rows are **shuffled** (fixed seed), so neither the file order nor `id`
reveals which dataset an email came from; any slice, like the first 500
rows, has a realistic mix of tickets and spam. Some
columns become parts of that email. Others are **ground truth**: they stay in
the CSV and are only used to score the pipeline afterwards.

## Columns at a glance

| Column | What it is | Sent through the mail server? |
|---|---|---|
| `id` | Row number, 1–34,801 | **Yes, as a tracking header** (`X-Dataset-Id`) |
| `source` | Which Kaggle dataset the row came from | **No.** It gives the labels away |
| `from` | Made-up sender address | **Yes**, as the `From` header (port 25 or IMAP only) |
| `subject` | Subject line | **Yes**, as the `Subject` header |
| `body` | Email text | **Yes**, as the `text/plain` body |
| `spam` | 1 = spam, 0 = not spam | **No.** Label |
| `department` | Routing label | **No.** Label |
| `reply` | A support agent's reference reply | **No.** Used to score auto-replies |

There is no `to` column: it's always `inbox@localmail.test`. See
[Sender and recipient](#sender-and-recipient).

## Each column

### `id`
A unique integer per row. It's the only link between an email in a mailbox and
its labels in the CSV, so it **must** travel with the message. Put it in a
custom header, `X-Dataset-Id: 123`, and optionally in the `Message-ID`
(`<email-123@dataset.localmail.test>`). The pipeline reads it only for logging
and scoring, never as model input.

### `source`
One of three values:

| Value | Rows | Has `department`? | Has `spam = 1`? |
|---|---|---|---|
| `multilang_tickets` | 16,338 | Yes, all rows | No |
| `spam_dataset` | 10,000 | No | 3,995 rows |
| `support_tickets` | 8,463 | No | No |

**Never put it in the email.** This isn't about privacy (everything runs
locally). It's label leakage: no email outside `spam_dataset` is spam, and
only `multilang_tickets` rows have a department. A model that could see
`source` would learn that shortcut instead of reading the email, and its
accuracy would be inflated. Keep `source` in the CSV and join it back by `id`
after the run, for example to report accuracy per source.

### `subject`
Median 20 characters, longest 234. **2,607 are empty**, kept on purpose because
real mail has empty subjects. **1,007 contain non-ASCII characters**
(emoji in spam subjects like `🔥WIN BIG NOW!!`). Python's `EmailMessage`
encodes them automatically (RFC 2047), so they go through the server unchanged.

### `body`
Never empty. Median 264 characters, longest 1,141. Sent as
`text/plain; charset=utf-8`. Things to know:

- **Anonymisation placeholders.** 607 ticket bodies contain tokens like
  `<name>`, `<tel_num>`, `<acc_num>`, left by the dataset author.
- **Template placeholders (fixed).** The support tickets were generated
  from templates with ~300 placeholder spellings (`{product_purchased}`,
  `{Product_id}`, `{error_message}`…). The build script fills them with the
  ticket's product or a realistic error message and removes the rest. 49
  code-like fragments (`{ int i; }`) are left in as pasted-code noise.
- **HTML fragments.** Some bodies contain `<br>`, `<p>`, `<div>`. They're
  sent as plain text, so they show up as literal tags. That's realistic mess,
  so we leave it.
- **No real HTML emails or attachments yet.** Every message is
  plain-text-only, so the pipeline's HTML and attachment handling isn't
  exercised by this dataset.

### `spam`
Ground truth for the spam filter: 3,995 spam (11%), 30,806 not spam. All spam
comes from `spam_dataset`. **Not sent.**

### `department`
Ground truth for routing: `billing`, `sales`, `support`, `hr`, `unclear`, or
empty. Only the 16,338 `multilang_tickets` rows have one; the 10 original
ticket queues are mapped to our departments in `scripts/build_dataset.py`.
`support` is 78% of labelled rows and **`marketing` has none yet**. Empty
means "no reliable label", not "unclear". **Not sent.**

### `reply`
The support agent's first reply from the ticket dataset, present for 16,335
`multilang_tickets` rows and empty everywhere else. It's the reference for
judging the system's auto-replies. 8,010 replies contain placeholders like
`<name>`. **Not sent** with the incoming email.

## Sender and recipient

Every email goes from our machine into our own mail server, so the original
datasets' sender addresses don't mean anything and were replaced:

- **`from`** (a column) is one of 1,000 made-up addresses,
  `customer0000@customer.test` to `customer0999@customer.test`. The build
  script assigns them at random from **one shared pool** for every row,
  whatever its source, with a fixed seed so every rebuild gives the same CSV.
  Every address appears in all three sources.
- **`To`** (not a column) is always `inbox@localmail.test`, the triage inbox,
  set by the sending script.

Why not just send everything as `inbox@localmail.test`?

- **Reply loops.** The pipeline auto-replies to the `From` address. If that's
  `inbox@`, every reply lands back in the triage inbox and gets processed
  again.
- **No shortcut.** The original datasets each had their own sender style
  (`@customer.test`, `@example.com`, random `@gmail.com`), which told a model
  which dataset, and so which labels, an email came from. One shared pool
  removes that hint.

**How it gets in:** the server has `SPOOF_PROTECTION=1`, so a logged-in
sender on port 587 may only use their own address as `From`. A made-up
customer address needs one of these instead:

- **SMTP on port 25, unauthenticated.** This is how outside mail arrives
  normally, and it accepts any `From` for a local recipient. SPF, DKIM, DMARC,
  Rspamd and SpamAssassin are all turned off in `mailserver.env`, so the
  server won't filter or tag our spam itself. The pipeline has to do that.
- **IMAP `APPEND`** straight into `inbox@`, the same pattern as
  [the classify-and-route example](../pipeline/overview.md#the-classify-and-route-pattern).
  It skips SMTP entirely, so no `Received` headers are added.

Customer addresses aren't on our domain, so a real auto-reply to one will
fail to deliver. When we build auto-replies, we'll either put the customer
pool on a local domain or capture outgoing replies instead of delivering them.

## Email fields the dataset doesn't have

The pipeline parses `from`, `to`, `date`, `subject`, `body`, `attachments`,
`headers`. Of those, the CSV has no:

| Field | How it gets filled |
|---|---|
| `to` | Always `inbox@localmail.test`, set by the sending script |
| `date` | `Date` header set by the sending script when it sends |
| `attachments` | None in this dataset; to come from synthetic emails |
| `headers` | `Message-ID`, `Received` etc. are added by the script and the server |

## Sending one row (sketch)

```python
import smtplib
from email.message import EmailMessage
from email.utils import formatdate

def send_row(row):
    msg = EmailMessage()
    msg["From"] = row["from"]                # made-up, shared pool
    msg["To"] = "inbox@localmail.test"
    msg["Subject"] = row["subject"]          # may be empty
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = f"<email-{row['id']}@dataset.localmail.test>"
    msg["X-Dataset-Id"] = str(row["id"])     # the only label-side column sent
    msg.set_content(row["body"])             # utf-8, encodes long/non-ASCII lines

    with smtplib.SMTP("mail.localmail.test", 25) as smtp:  # not 587: spoof protection
        smtp.send_message(msg)
```

!!! note "Not yet tested against the running server"
    The port-25 behaviour above comes from `mailserver.env` (spoof protection
    on, every content filter off). Confirm it with one message before
    sending all 34,801, and send in batches.
