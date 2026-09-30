#!/bin/bash
# Installs the Playwright CLI used by the playwright-cli skill in Claude Code on the web.
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

if ! command -v playwright-cli >/dev/null 2>&1; then
  npm install -g @playwright/cli@0.1.22 >/dev/null 2>&1
fi
