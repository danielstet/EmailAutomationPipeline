"""Build data/emails_clean.csv and data/department_histogram.png from the raw
Kaggle downloads in data/ (see data/README.md for where to get them).

Run from the repo root:  python scripts/build_dataset.py
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "data"
OUT_CSV = DATA / "emails_clean.csv"
OUT_PNG = DATA / "department_histogram.png"

DEPARTMENTS = ["billing", "sales", "support", "hr", "marketing", "unclear"]

# The multi-lang ticket queues, mapped onto our fake company's departments.
QUEUE_TO_DEPARTMENT = {
    "Technical Support": "support",
    "Product Support": "support",
    "IT Support": "support",
    "Service Outages and Maintenance": "support",
    "Customer Service": "support",
    "Billing and Payments": "billing",
    "Returns and Exchanges": "billing",
    "Sales and Pre-Sales": "sales",
    "Human Resources": "hr",
    "General Inquiry": "unclear",
}

# Senders come from ONE shared pool of made-up addresses, assigned at random
# to every row whatever its source, so the sender never hints at the labels.
# Fixed seed = the same CSV on every rebuild. No `to` column: it's always
# inbox@localmail.test, set by the sending script.
SENDER_POOL = [f"customer{i:04d}@customer.test" for i in range(1000)]
SEED = 42

COLUMNS = ["id", "source", "from", "subject", "body", "spam", "department", "reply"]


def clean_text(s: pd.Series) -> pd.Series:
    """Turn literal '\\n' sequences into real newlines and trim whitespace."""
    return s.fillna("").astype(str).str.replace("\\n", "\n", regex=False).str.strip()


def load_tickets() -> pd.DataFrame:
    """Multi-lang IT support tickets: English only, queue -> department."""
    df = pd.read_csv(DATA / "aa_dataset-tickets-multi-lang-5-2-50-version.csv")
    df = df[df["language"] == "en"].reset_index(drop=True)
    return pd.DataFrame({
        "source": "multilang_tickets",
        "subject": clean_text(df["subject"]),
        "body": clean_text(df["body"]),
        "spam": 0,
        "department": df["queue"].map(QUEUE_TO_DEPARTMENT),
        "reply": clean_text(df["answer"]),
    })


def load_spam() -> pd.DataFrame:
    """Spam / not-spam emails. Only the spam label is used, no department."""
    df = pd.read_csv(DATA / "spam_email_dataset.csv")
    return pd.DataFrame({
        "source": "spam_dataset",
        "subject": clean_text(df["subject"]),
        "body": clean_text(df["email_text"]),
        "spam": df["label"].astype(int),
        "department": "",
        "reply": "",
    })


def load_support() -> pd.DataFrame:
    """Customer support tickets: text only. Their Ticket Type labels are random
    (independent of the ticket subject), so they are not used."""
    df = pd.read_csv(DATA / "customer_support_tickets.csv")
    body = [
        desc.replace("{product_purchased}", product)
        for desc, product in zip(df["Ticket Description"], df["Product Purchased"])
    ]
    return pd.DataFrame({
        "source": "support_tickets",
        "subject": clean_text(df["Ticket Subject"]),
        "body": clean_text(pd.Series(body)),
        "spam": 0,
        "department": "",
        "reply": "",
    })


def build() -> pd.DataFrame:
    df = pd.concat([load_tickets(), load_spam(), load_support()], ignore_index=True)
    df = df[df["body"] != ""]
    df = df.drop_duplicates(subset=["subject", "body"]).reset_index(drop=True)
    df["department"] = df["department"].fillna("")
    df["id"] = range(1, len(df) + 1)
    rng = np.random.default_rng(SEED)
    df["from"] = rng.choice(SENDER_POOL, size=len(df))
    return df[COLUMNS]


def plot_departments(df: pd.DataFrame) -> None:
    labelled = df[df["department"] != ""]
    counts = labelled["department"].value_counts().reindex(DEPARTMENTS, fill_value=0)

    ink, muted, grid, bar = "#0b0b0b", "#52514e", "#e4e3df", "#2a78d6"
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
    fig.patch.set_facecolor("white")

    bars = ax.bar(counts.index, counts.values, width=0.55, color=bar, zorder=2)
    for rect, value in zip(bars, counts.values):
        ax.annotate(
            f"{value:,}" if value else "0 (none yet)",
            (rect.get_x() + rect.get_width() / 2, value),
            xytext=(0, 4), textcoords="offset points",
            ha="center", va="bottom", fontsize=9, color=ink,
        )

    ax.set_title(
        f"Emails per department (target variable), n = {len(labelled):,}",
        loc="left", fontsize=12, color=ink, pad=14,
    )
    ax.set_ylabel("Number of emails", color=muted, fontsize=9)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.tick_params(colors=muted, labelsize=9, length=0)
    ax.grid(axis="y", color=grid, linewidth=1, zorder=0)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(grid)
    fig.text(
        0.01, 0.01,
        "Source: English rows of the multi-lang tickets dataset, queues mapped to departments.",
        fontsize=7.5, color=muted,
    )
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(OUT_PNG)
    print(counts.to_string())


if __name__ == "__main__":
    data = build()
    data.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_CSV.name}: {len(data):,} rows")
    print(data.groupby("source").size().to_string())
    print("spam:", data["spam"].value_counts().to_dict())
    print("empty subject:", int((data["subject"] == "").sum()))
    plot_departments(data)
