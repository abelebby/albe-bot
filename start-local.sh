#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -x .venv/bin/python || ! -f build/index.html ]]; then
  echo "Local setup is incomplete: Python environment and frontend build are required."
  exit 1
fi
export PYTHONPATH="$PWD/backend"
export STATIC_DIR="$PWD/.local-tools/static"
mkdir -p "$STATIC_DIR"
cp -R "$PWD/backend/open_webui/static/." "$STATIC_DIR/"
# Use a persistent local key even with login disabled; Open WebUI needs it internally.
# Avoid the upstream container launcher, which requires Bash 4 (macOS ships Bash 3).
export WEBUI_SECRET_KEY="$(.venv/bin/python - <<'PY'
from pathlib import Path
import secrets
key = Path('.local-tools/webui-key')
key.parent.mkdir(exist_ok=True)
if not key.exists():
    key.write_text(secrets.token_hex(32))
    key.chmod(0o600)
print(key.read_text().strip())
PY
)"
exec .venv/bin/python -m uvicorn open_webui.main:app --host 127.0.0.1 --port 8080
