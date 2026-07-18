# Zylora frontend settings update

## Added

- Premium Zylora marketing homepage retained and connected to dynamic platform settings.
- `/login` local access portal.
- `/admin/sites/[slug]/settings` admin contact settings.
- `/sites/[slug]` public client landing pages.
- `/super-admin/settings` Zylora platform email settings.
- Admin and super-admin JSON APIs with Zod validation.
- Separate production write keys for admin and super-admin settings.
- Privacy, terms, and security routes.
- Persistent-directory configuration for the JSON settings adapter.
- Responsive styling for settings, legal, access, and client landing pages.

## Verified

```text
npm --prefix apps/web run typecheck  PASS
npm --prefix apps/web run build      PASS
```

## First routes to open

```text
http://localhost:3000/
http://localhost:3000/login
http://localhost:3000/admin/sites/demo-business/settings
http://localhost:3000/sites/demo-business
http://localhost:3000/super-admin/settings
```
