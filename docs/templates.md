# Templates and content

The application includes school, coaching centre, clinic, agency, and general
local-business template definitions. Websites are rendered from typed JSON
snapshots rather than arbitrary client HTML.

The constrained editor supports content, navigation, sections, visibility,
template selection, theme tokens, SEO metadata, and validation. Client-specific
paid code can be registered in `apps/web/src/client-overrides` without changing
other tenant templates.

Published snapshots are immutable. New changes are made in a draft and pass
through review and approval.
