"""EDA dashboard for the fake company's incoming email (M2).

Run from the repo root:  streamlit run app.py
"""
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "emails_clean.csv"
DEPARTMENTS = ["billing", "sales", "support", "hr", "marketing", "unclear"]
NO_LABEL = "(no label)"
SOURCES = {
    "multilang_tickets": "IT support tickets",
    "spam_dataset": "Spam dataset",
    "support_tickets": "Customer support tickets",
}
# Chart colours (validated categorical palette, slots 1 and 2).
BLUE, ORANGE = "#2a78d6", "#eb6834"

st.set_page_config(page_title="Email Automation Pipeline", page_icon="📧", layout="wide")


@st.cache_data
def load() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE, keep_default_na=False)
    df["department"] = df["department"].replace("", NO_LABEL)
    df["body_length"] = df["body"].str.len()
    df["spam_label"] = df["spam"].map({0: "Not spam", 1: "Spam"})
    return df


emails = load()
labelled_all = emails[emails["department"] != NO_LABEL]

# Baselines are fixed on the full dataset: they're the numbers M3 has to beat.
majority_dept = labelled_all["department"].mode()[0]
dept_baseline = (labelled_all["department"] == majority_dept).mean()
spam_baseline = (emails["spam"] == 0).mean()

# --- Sidebar filters ---------------------------------------------------------
st.sidebar.header("Filters")
sources = st.sidebar.multiselect(
    "Source dataset",
    options=list(SOURCES),
    default=list(SOURCES),
    format_func=SOURCES.get,
)
departments = st.sidebar.multiselect(
    "Department",
    options=DEPARTMENTS + [NO_LABEL],
    default=DEPARTMENTS + [NO_LABEL],
    help="'(no label)' = emails from sources without a reliable department label.",
)
spam_choice = st.sidebar.radio("Spam", ["All", "Spam only", "Not spam only"])

view = emails[emails["source"].isin(sources) & emails["department"].isin(departments)]
if spam_choice == "Spam only":
    view = view[view["spam"] == 1]
elif spam_choice == "Not spam only":
    view = view[view["spam"] == 0]
labelled = view[view["department"] != NO_LABEL]

st.sidebar.caption(f"Showing {len(view):,} of {len(emails):,} emails")

# --- Header + insight ---------------------------------------------------------
st.title("📧 Email Automation Pipeline: what's in the inbox")
st.success(
    f"**We found that {dept_baseline:.1%} of the labelled business email belongs to "
    f"support.** A model that always answers \"{majority_dept}\" is already "
    f"{dept_baseline:.1%} accurate, so overall accuracy will flatter any model. "
    "What matters to the operations manager is routing the small departments "
    "(billing, sales, hr) correctly, so we'll measure accuracy per department."
)

# --- Metrics ------------------------------------------------------------------
if view.empty:
    st.warning("No emails match these filters.")
    st.stop()

top_share = labelled["department"].value_counts(normalize=True) if not labelled.empty else None
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric(
    "Spam rate",
    f"{view['spam'].mean():.1%}",
    help="KPI the operations manager checks first: how much of the inbox is junk.",
)
m2.metric("Emails", f"{len(view):,}")
m3.metric(
    f"Largest department: {top_share.index[0]}" if top_share is not None else "Largest department",
    f"{top_share.iloc[0]:.1%}" if top_share is not None else "n/a",
    help="Share of the labelled emails in view that go to the biggest department.",
)
m4.metric(
    "Baseline: department",
    f"{dept_baseline:.1%}",
    help=f"Always predict '{majority_dept}' (the most common class), on all "
    f"{len(labelled_all):,} labelled emails. The M3 model must beat this.",
)
m5.metric(
    "Baseline: spam",
    f"{spam_baseline:.1%}",
    help=f"Always predict 'not spam', on all {len(emails):,} emails. "
    "The M3 spam filter must beat this.",
)

# --- Charts -------------------------------------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Where should the email go?")
    st.caption("Emails per department (labelled emails in the current filter).")
    counts = (
        labelled["department"].value_counts().reindex(DEPARTMENTS, fill_value=0)
        .rename_axis("department").reset_index(name="emails")
    )
    bars = alt.Chart(counts).mark_bar(
        color=BLUE, size=36, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
    ).encode(
        x=alt.X("department:N", sort=DEPARTMENTS, title=None, axis=alt.Axis(labelAngle=0)),
        y=alt.Y("emails:Q", title="Emails"),
        tooltip=["department", alt.Tooltip("emails:Q", format=",")],
    )
    labels = bars.mark_text(dy=-8, color="#52514e").encode(text=alt.Text("emails:Q", format=","))
    st.altair_chart((bars + labels).properties(height=320), width="stretch")

with right:
    st.subheader("Is spam different from real mail?")
    st.caption("Distribution of email body length, spam vs. not spam.")
    hist = alt.Chart(view).mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
        x=alt.X("body_length:Q", bin=alt.Bin(maxbins=40), title="Body length (characters)"),
        y=alt.Y("count():Q", title="Emails"),
        color=alt.Color(
            "spam_label:N",
            scale=alt.Scale(domain=["Not spam", "Spam"], range=[BLUE, ORANGE]),
            legend=alt.Legend(title=None, orient="top"),
        ),
        row=alt.Row("spam_label:N", title=None, header=alt.Header(labelAngle=0, labelAlign="left")),
        tooltip=["spam_label", alt.Tooltip("count():Q", title="emails", format=",")],
    ).properties(height=120).resolve_scale(y="independent")
    st.altair_chart(hist, width="stretch")

# --- Sample table ---------------------------------------------------------------
st.subheader("Sample of the cleaned data")
st.caption("First 50 emails in the current filter (rows are shuffled). Body cut to 150 characters.")
sample = view.head(50).assign(body=lambda d: d["body"].str.slice(0, 150))
st.dataframe(
    sample[["id", "source", "from", "subject", "body", "spam", "department"]],
    hide_index=True,
    width="stretch",
)
st.caption("Source: data/emails_clean.csv, built by scripts/build_dataset.py from three Kaggle datasets.")
