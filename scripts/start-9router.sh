#!/bin/bash
# Start 9Router in tray mode (keeps running after terminal closes).
# Dashboard: http://127.0.0.1:20128/dashboard

set -euo pipefail

if curl -sf http://127.0.0.1:20128/v1/models >/dev/null 2>&1; then
  echo "9Router already running at http://127.0.0.1:20128"
  exit 0
fi

echo "Starting 9Router..."
exec 9router --tray --skip-update --host 127.0.0.1 --no-browser
