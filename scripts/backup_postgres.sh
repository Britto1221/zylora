#!/usr/bin/env bash
set -Eeuo pipefail
: "${DATABASE_URL:?DATABASE_URL is required}"
: "${BACKUP_ENCRYPTION_PASSPHRASE:?BACKUP_ENCRYPTION_PASSPHRASE is required}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"
TMP="$BACKUP_DIR/zylora-$STAMP.dump"
OUT="$TMP.enc"
pg_dump --format=custom --no-owner --no-acl "$DATABASE_URL" > "$TMP"
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 200000 -pass env:BACKUP_ENCRYPTION_PASSPHRASE -in "$TMP" -out "$OUT"
sha256sum "$OUT" > "$OUT.sha256"
rm -f "$TMP"
find "$BACKUP_DIR" -type f -name 'zylora-*.dump.enc*' -mtime +"${BACKUP_RETENTION_DAYS:-30}" -delete
printf '%s\n' "$OUT"
