# EDA Conclusions

The conclusions from the EDA notebook `eda.ipynb` (repo root),
kept here so a teammate or a new Claude session can continue from the same point
without re-running it. Data: `data/emails_clean.csv`, 34,801 rows.

## Insight and baselines

**We found that 78.5% of the labelled business email belongs to `support`.** A
model that always answers "support" is already 78.5% accurate, so overall
accuracy flatters any model. For the operations manager the valuable part is
routing the small departments (billing 15%, sales 3%, hr 2%) correctly, so M3 is
scored per department and with macro-F1.

| Target | Baseline | Accuracy | Main metric (to beat) |
|---|---|---|---|
| `department` (16,338 labelled rows) | Always `support` | **78.5%** | macro-F1 **0.18** |
| `spam` (34,801 rows) | Always "not spam" | **88.5%** | spam precision **27.9%** (rule: body under 200 chars = spam, catches 99.5% of spam) |

Department → macro-F1 (every department counts equally). Spam → precision (a real
email lost in the spam folder is the costliest mistake), The precision bar is a "body under 200
characters = spam" rule (27.9%), since "always not spam" never flags anything.

## 1. Column types

- Text: `subject`, `body`, `reply`. Targets: `spam` (binary), `department` (categorical, 6 classes, empty = no label).
- Identifiers: `id` and `from`. `from` is technically categorical (1,000 made-up addresses, 19–60 emails each) but assigned at random, so it says nothing about the email: treated as an ID. `source` is categorical but describes where the row came from.
- **Model inputs are only `subject` and `body`.** `id`, `from`, `source` and `reply` are never inputs.
- No dates, so there are no time columns.

## 2. Data quality

| Check | Finding | Decision |
|---|---|---|
| Empty values | `subject` 7.5%, `department` 53.1%, `reply` 53.1%; `from`/`body` never empty | Not filled. Empty department = "no label", not `unclear` |
| Where the gaps are | Structural: department/reply empty for 100% of spam and support-ticket rows; empty subjects only in IT tickets (16%) | Route only on labelled rows; "no subject" is a fake not-spam signal |
| Exact duplicates | 0 left (6 removed in cleaning) | — |
| Same body, different subject | 121 rows (119 generated support tickets) | Kept: different emails sharing a template sentence |
| Broken generator fragments | 366 bodies (1.1%), all unlabelled support tickets: cut-off placeholders (`{product_p`) and code/JSON | Kept and flagged: no labels affected; revisit when synthetic mail replaces this source |
| Outliers | Body 6–1,141 chars; the long tail is detailed IT tickets | Kept: no impossible values |

## 3. Distributions

- **Spam:** 3,995 spam (11.5%) vs. 30,806 → imbalanced, both classes present.
- **Department:** support 78.5%, billing 14.8%, sales 3.1%, hr 2.1%, unclear 1.4%, **marketing 0** → very imbalanced; marketing must come from synthetic mail.
- **Spam is shorter:** median body 131 vs. 285 characters; almost no spam over ~200.
- **Departments look alike on the surface:** median length 338–452, 16–21% without subject → the router must read the body.

## 4. Correlation and leakage

- `body_length` ~ `body_words` = 0.98: redundant, keep one.
- `id` ~ everything = 0.00: the shuffle works, row order leaks nothing.
- **Leak: "!" in the subject has correlation 0.85 with spam** (74% of spam, 0% of real mail). Artifact of the synthetic spam data, so no features or prompts use it, and spam accuracy here is optimistic. `subject_upper_ratio` (0.56) is the same effect, weaker.
- Same artifact: spam bodies **never contain a digit** (average 0.00 vs. 0.57 in real mail), and every spam email has a subject.
- **Leak: `source` and `reply`** decide whether a row can be spam / has a department → never inputs.
- **Department vs. surface features:** all associations < 0.1 (length, digits, has_subject); `from` 0.25 is chance from 1,000 categories. No leak, no signal.
- **Signal is in the words:** "billing" in 37% of billing mail, "payment" 20%, "employee" 15% of hr mail.
- **Warning:** billing words appear in exactly 0% of the 13,923 non-billing emails. The text was probably generated from the label, so billing routing here will look easier than on real mail. `sales` and `unclear` have no marker words and will be the hard classes; labels are also noisy (integration questions labelled `billing`).
