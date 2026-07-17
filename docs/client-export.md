# Standalone Client Export

The standalone export creates a static ZIP for one tenant. It is intended for a
client's own developer or IT team and has no dependency on Zylora servers.

## Generate from the API

A super admin can use the export action on the client's Invoices tab or call:

```text
POST /api/v1/exports/{tenant_id}
```

The action is recorded in the audit log.

## Generate from the CLI

```bash
python scripts/export_client.py \
  --client_id=<TENANT_UUID> \
  --output_dir=exports
```

## Package contents

- `index.html`
- `styles.css`
- `.env.example` with blank optional third-party settings
- `README.md` with deployment instructions
- `export-manifest.json`

Templates use placeholders such as `{{CLIENT_NAME}}`, `{{PRIMARY_COLOR}}`,
`{{CONTACT_EMAIL}}`, and `{{SECTIONS}}`. Values are injected from the selected
tenant and its published website snapshot at export time.

## Security boundary

The ZIP excludes:

- Zylora application source code
- API keys and environment secrets
- PostgreSQL, OpenAI, RAG, intake, and administrative logic
- data from every other tenant
- client portal code
- AI chatbot integration
- Zylora lead-capture backend

The first export version is intentionally static. Contact information is
rendered, but a dynamic form backend is not exported. The client's team may
connect its own email or form service using the blank values documented in
`.env.example`.
