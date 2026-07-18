#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ! -f "apps/web/package.json" ]]; then
  echo "Run this script from the Zylora repository root." >&2
  exit 1
fi

STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR=".zylora-ui-backup/${STAMP}"

mkdir -p "${BACKUP_DIR}/apps/web/src/app/(marketing)"
mkdir -p "${BACKUP_DIR}/apps/web/src/app"

for file in \
  "apps/web/src/app/(marketing)/page.tsx" \
  "apps/web/src/app/globals.css" \
  "apps/web/src/app/layout.tsx"
do
  if [[ -f "${file}" ]]; then
    mkdir -p "${BACKUP_DIR}/$(dirname "${file}")"
    cp "${file}" "${BACKUP_DIR}/${file}"
  fi
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "apps/web/src/app/(marketing)"
cp "${SCRIPT_DIR}/apps/web/src/app/(marketing)/page.tsx" \
  "apps/web/src/app/(marketing)/page.tsx"
cp "${SCRIPT_DIR}/apps/web/src/app/globals.css" \
  "apps/web/src/app/globals.css"
cp "${SCRIPT_DIR}/apps/web/src/app/layout.tsx" \
  "apps/web/src/app/layout.tsx"

echo "Premium Zylora frontend installed."
echo "Backup: ${BACKUP_DIR}"
echo "Preview with: npm run dev:web"
