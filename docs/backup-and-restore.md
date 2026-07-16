# Backup and restore

Back up PostgreSQL with point-in-time recovery, enable object-storage versioning,
and retain published snapshots. Encrypt backup media and restrict restore access.

Quarterly restore test:

1. Provision an isolated database.
2. Restore the selected backup.
3. apply any pending migrations.
4. verify tenants, leads, credits, transactions, versions, and domains.
5. verify asset references and published sites.
6. document recovery time and any data gap.
