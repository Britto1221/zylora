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
