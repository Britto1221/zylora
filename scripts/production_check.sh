#!/usr/bin/env bash
set -Eeuo pipefail

fail=0

check() {
  if "$@"; then
    printf 'PASS: %s\n' "$*"
  else
    printf 'FAIL: %s\n' "$*" >&2
    fail=1
  fi
}

check git diff --check
check python -m compileall -q apps/api/app apps/worker/app packages/zylora-ai/zylora_ai
check bash -n scripts/production_check.sh

if command -v ruff >/dev/null 2>&1; then
  check bash -c 'cd apps/api && ruff check app tests'
fi

if command -v pytest >/dev/null 2>&1; then
  check bash -c 'cd apps/api && pytest'
fi

if command -v npm >/dev/null 2>&1 && [[ -d node_modules ]]; then
  check npm run typecheck:web
  check npm run build:web
fi

exit "$fail"
