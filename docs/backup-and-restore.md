# Backup and Restore

`backup_postgres.sh` creates a PostgreSQL custom-format dump, encrypts it with AES-256-CBC/PBKDF2, records a SHA-256 checksum, and enforces configurable retention. Store the encryption passphrase in a secret manager, never in Git.

Run:

```bash
export DATABASE_URL='postgresql://...?...sslmode=verify-full'
export BACKUP_ENCRYPTION_PASSPHRASE='from-secret-manager'
bash scripts/backup_postgres.sh
```

Restore into a separate database first:

```bash
export RESTORE_DATABASE_URL='postgresql://.../zylora_restore?sslmode=verify-full'
bash scripts/restore_postgres.sh backups/zylora-TIMESTAMP.dump.enc
```

The GitHub workflow verifies the backup/restore scripts against PostgreSQL. Production restores must also validate row counts, recent payments, credit balances, leads, published-site pointers, and object-storage references.
