# Getting Started

The mail server is [docker-mailserver](https://docker-mailserver.github.io/docker-mailserver/)
— a real Postfix + Dovecot stack (SMTP send, IMAP mailboxes) — living in
`mailserver/` at the repo root.

!!! note "Why not Stalwart?"
    We tried [Stalwart](https://stalw.art/) first. It's a newer, more
    "modern" mail server, but at the version available when we tried it, it
    had repeated wizard and OAuth-login bugs that cost far more time than
    they were worth for what's just a local test rig. docker-mailserver is
    years-old, widely deployed, and extensively documented — prefer it for
    any future local mail server needs in this project. Details in
    [Architecture Notes](architecture-notes.md).

## Quick start

```bash
cd mailserver
docker compose up -d
```

Mail data, logs, and config persist in `mailserver/docker-data/` (bind-mounted
into the containers, not Docker-managed volumes — except `mail-state`, see
[Architecture Notes](architecture-notes.md)), so the setup is identical for
everyone who clones the repo.

The container needs at least one mail account to exist within 120 seconds of
starting, or it shuts Dovecot down. Six test accounts are already committed
(`mailserver/docker-data/dms/config/postfix-accounts.cf` — see
[Accounts & Webmail](accounts-and-webmail.md)), so a fresh clone just works
with no account setup needed.

## One-time step: generate the TLS certificate

Private keys aren't committed to git (see `mailserver/.gitignore`) — commit
the generation script instead, not the keys themselves. Run once per clone:

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

=== "macOS / Linux"

    ```bash
    sudo sh -c 'echo "127.0.0.1 mail.localmail.test" >> /etc/hosts'
    ```

    On another LAN device, use the Docker host's LAN IP instead of
    `127.0.0.1`.

=== "Windows"

    Edit `C:\Windows\System32\drivers\etc\hosts` as Administrator and add:

    ```
    <Docker-host-LAN-IP> mail.localmail.test
    ```

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

`swaks` is already bundled inside the mailserver image — no local install
needed, just `docker exec` into the container.
