#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ! -d "apps" ]]; then
  echo "Run this script from the Zylora repository root." >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR=".zylora-web-backup/${STAMP}"

mkdir -p "${BACKUP_DIR}"
for item in package.json package-lock.json next.config.mjs tsconfig.json next-env.d.ts src data; do
  if [[ -e "apps/web/${item}" ]]; then
    mkdir -p "${BACKUP_DIR}/apps/web"
    cp -a "apps/web/${item}" "${BACKUP_DIR}/apps/web/"
  fi
done

mkdir -p apps/web
cp -a "${SCRIPT_DIR}/apps/web/." "apps/web/"
rm -rf apps/web/node_modules apps/web/.next
rm -f apps/web/tsconfig.tsbuildinfo

echo "Complete Zylora web application restored."
echo "Backup: ${BACKUP_DIR}"
echo "Next commands:"
echo "  npm --prefix apps/web install"
echo "  npm --prefix apps/web run dev"
