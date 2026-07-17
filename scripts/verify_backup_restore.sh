#!/usr/bin/env bash
set -Eeuo pipefail
: "${DATABASE_URL:?DATABASE_URL is required}"
: "${RESTORE_DATABASE_URL:?RESTORE_DATABASE_URL is required}"
FILE="$(bash scripts/backup_postgres.sh)"
bash scripts/restore_postgres.sh "$FILE"
SOURCE_TABLES="$(psql "$DATABASE_URL" -Atc "select count(*) from information_schema.tables where table_schema='public'")"
RESTORED_TABLES="$(psql "$RESTORE_DATABASE_URL" -Atc "select count(*) from information_schema.tables where table_schema='public'")"
[[ "$SOURCE_TABLES" = "$RESTORED_TABLES" ]] || { echo "Restore verification failed" >&2; exit 1; }
echo "Backup and restore verified: $RESTORED_TABLES tables"
