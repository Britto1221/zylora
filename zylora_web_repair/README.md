# Zylora complete web repair

This repair package restores the entire `apps/web` Next.js application, including:

- App Router root layout and global CSS
- Premium marketing landing page
- Login and legal pages
- Super-admin dashboard and settings
- Client-admin dashboard and landing-page settings
- Dynamic client public landing pages
- Settings API routes and persistent local JSON data
- Shared dashboard and admin components
- `package.json`, TypeScript config, and Next.js config

## Apply

Extract this folder inside the Zylora repository, then run from the repository root:

```bash
bash zylora_web_repair/apply-web-repair.sh
npm --prefix apps/web install
npm --prefix apps/web run dev
```
