# Disaster recovery

Priority order:

1. Stop writes when data integrity is uncertain.
2. Preserve logs and webhook payload hashes.
3. Restore PostgreSQL and object storage into an isolated environment.
4. reconcile payments, credit transactions, and notification jobs.
5. verify current published-version pointers and domains.
6. resume API, then worker, then public web traffic.
7. notify affected clients according to contractual and legal obligations.

Never repair an append-only credit history by editing old rows. Record a new
adjustment transaction.
