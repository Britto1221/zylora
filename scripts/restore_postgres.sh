#!/usr/bin/env bash
set -Eeuo pipefail
: "${RESTORE_DATABASE_URL:?RESTORE_DATABASE_URL is required}"
: "${BACKUP_ENCRYPTION_PASSPHRASE:?BACKUP_ENCRYPTION_PASSPHRASE is required}"
FILE="${1:?Pass the encrypted backup file}"
sha256sum -c "$FILE.sha256"
TMP="$(mktemp --suffix=.dump)"
trap 'rm -f "$TMP"' EXIT
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -pass env:BACKUP_ENCRYPTION_PASSPHRASE -in "$FILE" -out "$TMP"
pg_restore --clean --if-exists --no-owner --no-acl --dbname "$RESTORE_DATABASE_URL" "$TMP"
