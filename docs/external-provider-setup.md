# External Provider Setup

## Identity provider

Create an OpenID Connect application using authorization code flow with PKCE. Configure the exact production callback `/api/auth/callback`, logout URL, issuer, audience, JWKS, authorization and token endpoints. Add only verified owner addresses to `SUPER_ADMIN_EMAILS`. The API validates bearer tokens through JWKS; the web layer validates the token by calling `/auth/me` before creating the HTTP-only session cookie.

## Razorpay

Create test and live keys. Register `/api/v1/webhooks/razorpay`, store a distinct webhook secret, and subscribe to captured payment/order events. Zylora creates orders from server-owned credit packs; the browser cannot supply prices or credit values. Credits are added only after a verified captured-payment webhook.

## WhatsApp Cloud API

Verify the Meta business, phone number, and templates. Register GET/POST `/api/v1/webhooks/whatsapp`. Configure the app secret, verification token, permanent access token, phone number ID and API version. Run a real status test for sent, delivered, read and failed callbacks.

## Storage and malware scanning

Use an S3-compatible private bucket. Prefer AWS GuardDuty Malware Protection for S3 or deploy ClamAV. Uploads start in PENDING/SCANNING state and are unavailable until CLEAN. Configure lifecycle retention and object versioning.

## Monitoring

Create Sentry projects for the API and worker and configure `SENTRY_DSN`. Configure `ALERT_WEBHOOK_URL` for an operator-controlled Slack, Teams, PagerDuty or compatible endpoint. Verify a staging exception reaches both destinations.
