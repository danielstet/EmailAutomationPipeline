# Local Mail Server (LAN-only, testing)

A real [docker-mailserver](https://docker-mailserver.github.io/docker-mailserver/)
stack (Postfix + Dovecot) for local-network testing of the email automation
pipeline. Not hardened, not for internet exposure.

Full documentation — setup, accounts, webmail, architecture notes, the
classify-and-route pattern for the pipeline — lives in the project's
[MkDocs site](../docs/mail-server/getting-started.md) (`docs/` at the repo
root; run `docker run --rm -it -p 8000:8000 -v "${PWD}/..:/docs" squidfunk/mkdocs-material`
from here, or see `../mkdocs.yml`).

Quick start:

```bash
docker compose up -d
```

See [`docs/mail-server/getting-started.md`](../docs/mail-server/getting-started.md)
for the one-time TLS cert generation step and hosts-file requirement needed
before this works.
