# Manual Provider Actions

These steps cannot be completed by repository code:

1. Create and verify the legal business and support contact information.
2. Obtain legal review of privacy, terms, refund, cookie and service-agreement text.
3. Create the OIDC application and enter the production redirect/logout URLs.
4. Set the real `SUPER_ADMIN_EMAILS` value.
5. Complete Razorpay KYC, enable required payment methods, create keys and webhook secret.
6. Complete Meta Business and WhatsApp verification and obtain template approval.
7. Create private object storage and enable GuardDuty scanning or operate ClamAV.
8. Create managed PostgreSQL/Redis services with TLS and apply migrations/RLS.
9. Create Sentry and operator alert destinations.
10. Run DAST, load, backup-restore and provider sandbox tests against staging.
