# Local Mail Server (LAN-only, testing)

A real [docker-mailserver](https://docker-mailserver.github.io/docker-mailserver/) stack
(Postfix + Dovecot) for local-network testing of the email automation pipeline —
real SMTP send, real IMAP mailboxes, real move-between-mailboxes. Not hardened,
not for internet exposure.

We moved to this from an earlier attempt with Stalwart, which turned out too
immature (multiple wizard/login bugs) for what's just a local test rig. This
project is years-old, widely deployed, and far better documented — pick this
over Stalwart for any future local mail server needs here.

## Quick start

```bash
cd mailserver
docker compose up -d
```

Mail data, logs, and config persist in `docker-data/` inside this folder
(bind-mounted, not Docker-managed volumes — except `mail-state`, see
[Known gotchas](#known-gotchas-macos-docker-desktop) below), so the setup is
identical for everyone who clones the repo.

The container needs at least one mail account to exist within 120 seconds of
starting, or it shuts Dovecot down. The four accounts below are already
committed (`docker-data/dms/config/postfix-accounts.cf`), so a fresh clone
just works — no account setup needed.

**The one thing you do need to regenerate yourself:** the TLS certificate.
Private keys aren't committed to git (see `.gitignore`). One-time setup:

```bash
cd mailserver
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --volume "${PWD}/docker-data/dms/custom-certs/:/tmp/step-ca/" \
  --workdir "/tmp/step-ca/" \
  --entrypoint "/tmp/step-ca/generate-certs.sh" \
  smallstep/step-ca

mkdir -p docker-data/dms/config/ssl/demoCA
cp docker-data/dms/custom-certs/mail.localmail.test-cert.pem docker-data/dms/config/ssl/
cp docker-data/dms/custom-certs/mail.localmail.test-key.pem docker-data/dms/config/ssl/
cp docker-data/dms/custom-certs/demoCA/cacert.pem docker-data/dms/config/ssl/demoCA/
```

Then `docker compose up -d`.

## Hosts file requirement

The server's hostname (`mail.localmail.test`) isn't real DNS, so any machine
that wants to connect — including the Docker host itself — needs a hosts-file
entry:

- **macOS / Linux** (`/etc/hosts`):
  ```bash
  sudo sh -c 'echo "127.0.0.1 mail.localmail.test" >> /etc/hosts'
  ```
  (On another LAN device, use the Docker host's LAN IP instead of `127.0.0.1`.)
- **Windows** (`C:\Windows\System32\drivers\etc\hosts`, edit as Administrator):
  ```
  <Docker-host-LAN-IP> mail.localmail.test
  ```

## Accounts

All four share the password **`TestPass123!`** (local test server only —
never reuse this anywhere real):

| Address | Role |
|---|---|
| `inbox@localmail.test` | Triage inbox — where the pipeline reads incoming test mail |
| `sales@localmail.test` | Fake department |
| `support@localmail.test` | Fake department |
| `billing@localmail.test` | Fake department |
| `hr@localmail.test` | Fake department |
| `marketing@localmail.test` | Fake department |

Add more: `docker exec mailserver setup email add newuser@localmail.test 'TestPass123!'`

## Ports

| Port | Purpose |
|------|---------|
| 25   | SMTP (server-to-server) |
| 465  | SMTPS (implicit TLS submission) |
| 587  | SMTP submission (STARTTLS) |
| 143  | IMAP (STARTTLS) |
| 993  | IMAPS (implicit TLS) |

## Sending a test email

```bash
docker exec mailserver swaks --to inbox@localmail.test \
  --from inbox@localmail.test \
  --server localhost:587 \
  --auth-user inbox@localmail.test \
  --auth-password 'TestPass123!' \
  --tls \
  --header "Subject: Test" \
  --body "Hello"
```

(`swaks` is already bundled inside the mailserver image — no local install
needed, just `docker exec` into the container.)

## The classify-and-route pattern (for the Ollama pipeline)

This is how the pipeline should move a message from the triage inbox into a
department mailbox: fetch the raw message over IMAP, classify it, `APPEND`
the untouched raw message into the destination mailbox, then delete the
original. This preserves the real MIME/header structure — the message looks
exactly like a normal email to whoever reads it next.

```python
import imaplib, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE  # self-signed cert, LAN testing only

# 1. Fetch the raw message from the triage inbox
src = imaplib.IMAP4('mail.localmail.test', 143)
src.starttls(ssl_context=ctx)
src.login('inbox@localmail.test', 'TestPass123!')
src.select('INBOX')
typ, data = src.search(None, 'ALL')
msg_id = data[0].split()[0]
typ, msg_data = src.fetch(msg_id, '(RFC822)')
raw_message = msg_data[0][1]

# 2. Classify (this is where Ollama's decision plugs in)
dest_user = 'billing@localmail.test'

# 3. Append the real, untouched message into the destination mailbox
dst = imaplib.IMAP4('mail.localmail.test', 143)
dst.starttls(ssl_context=ctx)
dst.login(dest_user, 'TestPass123!')
dst.append('INBOX', None, None, raw_message)
dst.logout()

# 4. Remove from the triage inbox (completes the "move")
src.store(msg_id, '+FLAGS', '\\Deleted')
src.expunge()
src.logout()
```

Writing a reply follows the normal pattern: compose a MIME message (e.g. with
Python's `email.message.EmailMessage`) and send it via SMTP (port 587,
STARTTLS, same auth) — see the swaks example above for the equivalent raw
SMTP flow.

## Known gotchas (macOS Docker Desktop)

`/var/mail-state` (Postfix's runtime queue/locks/sockets) is a **named Docker
volume**, not a bind mount, unlike everything else. Bind-mounting it breaks
Postfix startup on Docker Desktop for Mac with `chmod socket private/smtpd:
Invalid argument` — Unix domain sockets don't survive the macOS↔Linux-VM
filesystem bridge. See [docker-mailserver#3648][gh-3648]. It's not real mail
data, so losing it on container recreation is harmless.

Anti-spam/anti-spoofing layers (OpenDKIM, OpenDMARC, policyd-spf, Amavis) are
disabled in `mailserver.env` — they're meaningless for a domain with no real
public DNS and just add things that could break for no benefit here.

[gh-3648]: https://github.com/docker-mailserver/docker-mailserver/issues/3648
