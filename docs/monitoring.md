# Monitoring

Monitor:

- `/api/v1/health`,
- `/api/v1/ready`,
- Prometheus metrics,
- API error rates and latency,
- queue depth and failed worker jobs,
- webhook failures and duplicates,
- payment/credit mismatches,
- expiring domains,
- low credit balances,
- database connection pool saturation,
- backup completion and restoration tests.

Configure Sentry with PII disabled. Logs must not include access tokens, API
keys, payment-card data, or full private message content.
