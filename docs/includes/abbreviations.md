*[IMAP]: Internet Message Access Protocol — the protocol mail clients use to read, organize, and move messages in mailboxes stored on a server.
*[SMTP]: Simple Mail Transfer Protocol — the protocol used to send/relay email between servers and clients.
*[STARTTLS]: A command that upgrades a plain-text connection to an encrypted TLS connection, used by SMTP/IMAP on their non-implicit-TLS ports.
*[TLS]: Transport Layer Security — the encryption protocol that secures a connection (the modern successor to SSL).
*[SSL]: Secure Sockets Layer — the predecessor to TLS; the term is still used colloquially/in config even when TLS is what's actually in use.
*[MIME]: Multipurpose Internet Mail Extensions — the format standard for email bodies/attachments/headers (how a message is actually structured on the wire).
*[DNS]: Domain Name System — translates domain names to IP addresses and hosts other records (MX, SPF, DKIM, DMARC) mail servers rely on.
*[SPF]: Sender Policy Framework — a DNS record listing which servers are allowed to send mail for a domain, used to detect spoofing.
*[DKIM]: DomainKeys Identified Mail — cryptographically signs outgoing mail so receivers can verify it wasn't altered and really came from the claimed domain.
*[DMARC]: Domain-based Message Authentication, Reporting and Conformance — a DNS policy telling receivers what to do when SPF/DKIM checks fail.
*[CA]: Certificate Authority — issues TLS certificates; browsers/clients trust a cert only if it's signed by a CA they already trust (our local CA is self-signed and not publicly trusted).
*[FQDN]: Fully Qualified Domain Name — a complete domain name identifying a host (e.g. `mail.localmail.test`), as opposed to a bare hostname.
*[LAN]: Local Area Network — a private network (e.g. your home/office Wi-Fi), as opposed to the public internet.
*[CSRF]: Cross-Site Request Forgery — an attack where a malicious site tricks your browser into making an unwanted authenticated request; the error we hit was this protection rejecting a conflicting second login.
*[OAuth]: An authorization protocol that lets an app get limited access to an account without handling the password directly, used for Stalwart's webui login.
*[JMAP]: JSON Meta Application Protocol — a modern JSON-based alternative to IMAP/SMTP (used by Stalwart's web interface internally).
*[SQLite]: A lightweight, file-based database engine — what Roundcube uses by default for its own settings storage (not mail itself).
*[UI]: User Interface — the part of an application a human interacts with directly (e.g. Roundcube's webmail UI).
*[API]: Application Programming Interface — a defined way for programs to talk to each other (e.g. the pipeline calling Ollama).
