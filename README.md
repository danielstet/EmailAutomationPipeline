# EmailAutomationPipeline

A local test rig for an email automation pipeline: a real mail server
(SMTP + IMAP) to develop and test against, plus a planned LangGraph +
LangChain + Ollama pipeline for classifying and routing incoming mail.

Full documentation lives in [`docs/`](docs/index.md) (MkDocs — see
[`mkdocs.yml`](mkdocs.yml)). Preview locally:

```bash
docker run --rm -it -p 8000:8000 -v "${PWD}:/docs" squidfunk/mkdocs-material
```

Then open <http://localhost:8000>.