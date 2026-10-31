# Email Automation Pipeline

A local, LAN-only test environment for an email automation pipeline: a real
mail server to send/receive against, plus a planned
[LangGraph](https://langchain-ai.github.io/langgraph/) +
[LangChain](https://www.langchain.com/) pipeline that uses a local
[Ollama](https://ollama.com/) model to classify incoming mail, route it to
the right department, and draft replies.

## What's built so far

- **A real mail server** — [docker-mailserver](https://docker-mailserver.github.io/docker-mailserver/)
  (Postfix + Dovecot), with real SMTP send and IMAP mailboxes. See
  [Getting Started](mail-server/getting-started.md).
- **A webmail UI** ([Roundcube](https://roundcube.net/)) for manually
  inspecting mailboxes in a browser. See
  [Accounts & Webmail](mail-server/accounts-and-webmail.md).
- **Six test mailboxes** — one triage inbox plus five fake departments — to
  exercise a realistic "classify and route" workflow.

## What's planned

A LangGraph graph where one node reads mail (over IMAP) and hands it to a
LangChain chain, which calls a local Ollama model; the model's response
decides which graph node runs next — e.g. moving the message into a
department mailbox, or drafting and sending a reply. LangSmith traces the
whole run. See [Pipeline Overview](pipeline/overview.md) for the intended
shape of this, and the IMAP read/move/send pattern it will build on.

## Why this exists

Testing an email automation pipeline against a real mailbox (not a mock)
means the pipeline has to handle actual MIME messages, actual IMAP folder
semantics, and actual SMTP delivery — the same primitives it'll use in
production, just pointed at a disposable local server instead of a real
mail provider.

!!! warning "Local network only"
    Everything here — the mail server, its self-signed TLS cert, the
    disabled anti-spam layers — is configured for an isolated local test
    rig. None of it is hardened for, or should be exposed to, the public
    internet.

## Previewing these docs locally

```bash
docker run --rm -it -p 8000:8000 -v "${PWD}:/docs" squidfunk/mkdocs-material
```

Then open <http://localhost:8000>.
