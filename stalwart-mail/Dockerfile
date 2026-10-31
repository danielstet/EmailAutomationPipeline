# Stalwart Mail Server — LAN-only testing image
#
# This is a thin wrapper around the official Stalwart image, pinned to a
# known-good major version and documented for local-network use only.
# Do NOT expose this container to the public internet (no real TLS cert,
# no hardened auth, no anti-abuse rules).
#
# Build:
#   docker build -t local-stalwart .
#
# Run (standalone, without compose):
#   docker volume create stalwart-etc
#   docker volume create stalwart-data
#   docker run -d --name stalwart --init --restart unless-stopped \
#     -p 25:25 -p 465:465 -p 587:587 -p 993:993 -p 995:995 \
#     -p 4190:4190 -p 443:443 -p 8080:8080 \
#     -v stalwart-etc:/etc/stalwart \
#     -v stalwart-data:/var/lib/stalwart \
#     local-stalwart
#
# Prefer `docker compose up -d` using the docker-compose.yml next to this file.

FROM stalwartlabs/stalwart:v1

LABEL description="Stalwart mail server (SMTP/IMAP/POP3/JMAP) for local-network-only testing" \
      org.opencontainers.image.source="https://github.com/stalwartlabs/stalwart"

# Config (/etc/stalwart) and mail data (/var/lib/stalwart) must survive
# container recreation — the setup wizard writes config.json here on first run.
VOLUME ["/etc/stalwart", "/var/lib/stalwart"]

# 25    SMTP (inbound relay between servers)
# 465   SMTPS (implicit TLS submission)
# 587   SMTP submission (STARTTLS) — enable the listener in the admin UI if needed
# 993   IMAPS
# 995   POP3S
# 4190  ManageSieve
# 443   HTTPS / JMAP / admin UI (post-setup)
# 8080  Plain-HTTP setup wizard (first run only, no brute-force protection)
EXPOSE 25 465 587 993 995 4190 443 8080
