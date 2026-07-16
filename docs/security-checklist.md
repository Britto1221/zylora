# Security Checklist

Before production:

- Replace development header authentication.
- Configure email verification and secure password reset.
- Require reauthentication for sensitive actions.
- Use HTTPS.
- Encrypt API credentials.
- Mask secrets in logs.
- Verify Razorpay/Stripe webhooks.
- Verify WhatsApp webhooks.
- Add rate limiting and bot protection.
- Apply PostgreSQL RLS.
- Add backup and recovery tests.
- Add audit logs.
- Add file validation and malware scanning.
