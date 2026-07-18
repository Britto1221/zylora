# Zylora Premium Frontend

This package replaces the minimal Zylora marketing page with a complete premium
Next.js landing page using the existing app-router structure.

## Files

Copy these files into the matching paths in your Zylora repository:

- `apps/web/src/app/(marketing)/page.tsx`
- `apps/web/src/app/globals.css`
- `apps/web/src/app/layout.tsx`

No additional npm dependencies are required.

## Preview

From the Zylora repository root:

```bash
npm install
npm run dev:web
```

Open:

```text
http://localhost:3000
```

## Notes

- Existing backend, dashboard, API, authentication, and route logic are untouched.
- The `Sign in` link targets `/login`.
- Footer legal links target `/privacy`, `/terms`, and `/security`; create these routes
  or replace the URLs if they do not exist yet.
- The CTA email currently uses `hello@zylora.ai`; replace it with your real address.

## Landing-page contact settings

The frontend now includes two separate settings flows:

- Client admin: `/admin/sites/<site-slug>/settings`
  - Updates the business name, public email, phone number, and address.
  - Changes appear on `/sites/<site-slug>`.
- Zylora super admin: `/super-admin/settings`
  - Updates Zylora's own public contact email.
  - Changes appear in the main landing-page CTA and footer.

Use `/login` as the local access portal. The included demo routes are:

- `/admin/sites/demo-business/settings`
- `/sites/demo-business`
- `/super-admin/settings`

### Protect settings writes

Local development allows updates when access-key environment variables are absent.
Production requires:

```bash
ZYLORA_ADMIN_SETTINGS_KEY=<long-random-key>
ZYLORA_SUPER_ADMIN_SETTINGS_KEY=<different-long-random-key>
```

The included storage adapter writes JSON files under `apps/web/data` by default.
For a server with a persistent volume, set:

```bash
ZYLORA_SETTINGS_DATA_DIR=/var/lib/zylora/settings
```

Serverless filesystems such as Vercel's runtime storage are not durable. Before a
serverless production launch, replace the file-backed functions in
`apps/web/src/lib/site-settings.ts` with PostgreSQL or another persistent database.
