from pathlib import Path

import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "data" / "sample_emails.csv"

st.set_page_config(page_title="Email Automation Pipeline", page_icon="📧")

st.title("📧 Email Automation Pipeline")
st.markdown(
    "**Start-ups and small companies** suffer from **expensive employee time being "
    "spent on small, repetitive jobs like sorting, forwarding and answering email**, "
    "and we'll build **an AI automation system that filters, routes and responds to "
    "company email** using **local AI models (Ollama) orchestrated with LangGraph "
    "and LangChain**."
)

st.info("Coming soon: dashboard + model")

st.subheader("Sample of incoming mail")
emails = pd.read_csv(DATA_FILE)
st.dataframe(emails.head(5), hide_index=True)
st.caption(f"{len(emails)} sample emails · source: data/sample_emails.csv")
