#!/usr/bin/env bash
set -Eeuo pipefail
if [[ ! -d apps/web/src ]]; then
  echo 'Run this script from the Zylora repository root.' >&2
  exit 1
fi
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p apps/web/src/components/dashboard
cp "$SCRIPT_DIR/apps/web/src/components/dashboard/dashboard-shell.tsx" apps/web/src/components/dashboard/dashboard-shell.tsx
rm -rf apps/web/.next
echo 'Dashboard component restored.'
echo 'Run: npm --prefix apps/web run dev'
