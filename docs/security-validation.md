# Security Validation

- API authorization is verified twice: membership checks in FastAPI and PostgreSQL RLS.
- Client viewers can read permitted tenant data but cannot mutate content, leads, notifications, credentials, assets, payments or publishing state.
- Public routes validate a published site before setting the constrained public tenant context.
- Prices, credit amounts, roles and publication rights are never trusted from the browser.
- Payment and notification side effects use idempotency keys.
- Uploads reject active content, verify byte signatures and remain quarantined pending malware results.
- Production requires PostgreSQL and Redis TLS.

Run the API security tests:

```bash
cd apps/api
pytest tests/security tests/unit/test_storage_security.py tests/unit/test_production_tls.py
```

Trigger DAST and load workflows only against an isolated staging environment with synthetic data.
