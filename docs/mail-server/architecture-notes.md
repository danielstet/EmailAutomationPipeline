# Architecture Notes

Decisions and gotchas worth knowing before changing this setup.

## Why docker-mailserver over Stalwart

Stalwart was tried first — newer, "all-in-one" (SMTP/IMAP/JMAP in one
binary), with a setup wizard. In practice, the version available at the
time repeatedly failed partway through that wizard:

- The wizard wrote partial config to disk on each step but only committed a
  complete config on a successful final "Finish setup" — any failure bounced
  back to step 1 with a confusing "item with the same key already exists"
  error and no indication what actually failed.
- Setting a fixed recovery-admin password (`STALWART_RECOVERY_ADMIN`) before
  completing first-run setup collided with the wizard's own admin-account
  creation.
- After setup did complete, the webui's OAuth login flow had its own
  hostname-handling bug (`Unknown client id`, then `Client metadata
  documents are disabled`) that required digging into the minified webui JS
  bundle to even understand.

None of this is a knock on Stalwart as a project — it's young (v1.0 shipped
days before we tried it) and these are the kind of rough edges new software
has. It's just not worth fighting for a local test rig. docker-mailserver
is years-old, widely deployed, and extensively documented; every issue we
hit with it had a known, documented fix within a search or two.

## The `mail-state` volume (macOS Docker Desktop)

`/var/mail-state` (Postfix's runtime queue/locks/sockets) is a
**Docker-managed named volume**, not a bind mount, unlike everything else
in `compose.yaml`. Bind-mounting it breaks Postfix startup on Docker Desktop
for Mac with:

```
fatal: chmod socket private/smtpd: Invalid argument
```

Unix domain sockets don't survive the macOS↔Linux-VM filesystem bridge that
Docker Desktop uses for bind mounts. This is a
[known upstream issue](https://github.com/docker-mailserver/docker-mailserver/issues/3648).
The documented fix is switching Docker Desktop's file-sharing backend
(VirtioFS ↔ gRPC-FUSE) globally, but that's an invasive host-wide setting.
Since `/var/mail-state` holds no real mail data, making it a named volume
instead sidesteps the bug entirely with no cost — losing it on container
recreation is harmless.

## The Roundcube TLS hostname alias

The self-signed cert's SAN covers `localmail.test` and `mail.localmail.test`
— not `mailserver`, the Docker Compose service name. If Roundcube connected
to the mailserver container as `mailserver` (the natural choice on the
internal Docker network), TLS hostname verification would fail.

Fix: the `mailserver` service declares a network alias of
`mail.localmail.test`, so other containers can reach it by the exact name
the cert was issued for. Roundcube's TLS peer verification is *also*
disabled (`tls.inc.php`) since the CA itself is a throwaway local one, not
publicly trusted — the hostname fix alone isn't sufficient, both pieces are
needed.

## Anti-spam/anti-spoofing layers are disabled

OpenDKIM, OpenDMARC, policyd-spf, and Amavis are all turned off in
`mailserver.env`. These mechanisms work against public DNS (SPF/DKIM
records, DMARC policy) which `localmail.test` doesn't have — leaving them on
would add moving parts that could fail or add latency with no real benefit
on an isolated LAN test rig.
