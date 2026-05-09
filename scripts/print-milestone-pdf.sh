#!/usr/bin/env bash
# Regenerate Milestone-2.pdf from reports/Milestone-2-print.html (Chrome headless).
# Requires Google Chrome under /Applications (macOS).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
export TMPDIR="${TMPDIR:-$ROOT/.wf-tmp}"
mkdir -p "$TMPDIR" "$ROOT/.chrome-user-data"
UD="$ROOT/.chrome-user-data"
rm -f "$UD/SingletonLock" "$UD/SingletonSocket" "$UD/SingletonCookie" 2>/dev/null || true
HTML="$ROOT/reports/Milestone-2-print.html"
PDF="$ROOT/Milestone-2.pdf"
"$CHROME" --headless=new --disable-gpu --no-first-run \
  --user-data-dir="$UD" \
  --no-pdf-header-footer \
  --print-to-pdf="$PDF" \
  "file://$HTML"
echo "Wrote $PDF"
