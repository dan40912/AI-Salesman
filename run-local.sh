#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/uvicorn ]; then
  echo '請先依 README 建立 .venv 並安裝 backend/requirements.txt。'
  exit 1
fi
exec .venv/bin/uvicorn backend.app:app --host 127.0.0.1 --port 8000 --no-access-log
