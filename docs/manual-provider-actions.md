# Manual provider actions

These actions require access to external dashboards and cannot be completed by
source code alone.

## Identity provider

- Create the OIDC application.
- Add web and API redirect/logout URLs.
- configure issuer, audience, and JWKS URL.
- invite or provision the production super admin.

## Razorpay

- Complete account and international-payment verification.
- create live keys.
- register the payment webhook URL and secret.
- configure settlement and tax/accounting information.

## WhatsApp Cloud API

- Verify Meta Business.
- register a phone number.
- create and approve business and visitor templates.
- register webhook verification and status URLs.
- configure access token, app secret, and phone-number ID.

## Domains

- Purchase domains using client legal details.
- configure wildcard platform DNS.
- add custom-domain DNS records.
- verify SSL and preferred-domain redirects.

## Storage and email

- create the S3-compatible bucket and least-privilege credentials.
- configure malware scanning.
- verify the email sending domain and create the provider key.

## Operations

- create production PostgreSQL and Redis.
- configure Sentry and alert routing.
- configure encrypted backups and restoration drills.
- add GitHub repository secrets and deployment credentials.
