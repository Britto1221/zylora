# Landing-page settings

## Client admin settings

Route:

```text
/admin/sites/<site-slug>/settings
```

Editable values:

- Business name
- Public email address
- Phone number
- Address

Public route:

```text
/sites/<site-slug>
```

The API validates all values with Zod and revalidates the public route after a
successful update.

## Zylora super-admin settings

Route:

```text
/super-admin/settings
```

Editable value:

- Zylora public contact email

The email is used in the homepage CTA and footer.

## Authorization

Write operations use separate environment keys:

```text
ZYLORA_ADMIN_SETTINGS_KEY
ZYLORA_SUPER_ADMIN_SETTINGS_KEY
```

In local development, settings can be saved without keys when the variables are
unset. In production, missing keys return `503`, and incorrect keys return `401`.
This is a standalone protection layer for the current frontend-only build. Replace
it with the platform's authenticated role and tenant authorization before full
production rollout.

## Persistence

The current adapter uses JSON files. By default they are stored in `apps/web/data`.
Set `ZYLORA_SETTINGS_DATA_DIR` to a writable persistent mounted directory on a
traditional server.

Do not rely on runtime filesystem writes for serverless deployment. Migrate the
store to PostgreSQL before deploying these settings features to a serverless host.
