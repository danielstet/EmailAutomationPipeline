# Accounts & Webmail

## Accounts

Local test server only — never reuse this password anywhere real:

| Address | Password | Role |
|---|---|---|
| `inbox@localmail.test` | `TestPass123!` | Triage inbox — where the pipeline reads incoming test mail |
| `sales@localmail.test` | `TestPass123!` | Fake department |
| `support@localmail.test` | `TestPass123!` | Fake department |
| `billing@localmail.test` | `TestPass123!` | Fake department |
| `hr@localmail.test` | `TestPass123!` | Fake department |
| `marketing@localmail.test` | `TestPass123!` | Fake department |

Add more:

```bash
docker exec mailserver setup email add newuser@localmail.test 'TestPass123!'
```

## Webmail UI (Roundcube)

A browser-based inbox for actually looking at mail, instead of only
scripting IMAP: **<http://localhost:8080>**, log in with any address above.

It connects to the mailserver container over the internal Docker network as
`mail.localmail.test` (a network alias on the `mailserver` service matching
the TLS cert's hostname) with peer verification disabled
(`mailserver/docker-data/roundcube/config/tls.inc.php`) — necessary because
the cert is self-signed by our own throwaway local CA, not a publicly
trusted one. See [Architecture Notes](architecture-notes.md) for why the
hostname alias matters here.

Roundcube's own SQLite settings database lives in
`mailserver/docker-data/roundcube/db/` (gitignored — regenerates itself on
first run, nothing to set up).

!!! tip "Logged into two accounts at once"
    Roundcube ties your login to one session cookie per browser, so opening
    a second tab and logging into a different account breaks the first
    session with a CSRF "Request check failed" error. Open the second
    account in an Incognito/Private window instead (or a different
    browser/profile) — separate cookie jar, both stay logged in
    simultaneously.
