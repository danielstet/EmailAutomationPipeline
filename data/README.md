# Data

Our data is **email**: unstructured messages arriving at the local mail server
(see the root [README](../README.md#data-source)). The pipeline parses each
message into the same fields: `from`, `to`, `date`, `subject`, `body`,
`attachments`, `headers`.

## Files here

- `sample_emails.csv` is a small, hand-written sample of the fake company's
  incoming mail, used by `app.py` for a preview. Its columns are `from`, `to`,
  `date`, `subject`, `body`, `spam` (0/1) and `department` (empty for spam).
  Some values are deliberately missing, such as an empty subject, the way they
  are in real email.

## Where the full data comes from

1. **Public Kaggle datasets** (spam, customer support tickets, HR emails,
   marketing, email tone). They're listed in
   [this Google Doc](https://docs.google.com/document/d/1PUPexD2djFNNJ2YQwhDMbW08m1U5ldpLtCQqNLAMqP4/edit?usp=sharing),
   which is still being checked. Download them from Kaggle into this folder.
2. **Synthetic emails** generated for the fake company.

Both are sent into the mail server as real email. Large downloaded files are
not committed to git (see `.gitignore`); only small samples live here.
