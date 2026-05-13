#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/.."

PORT=8000
URL="http://localhost:$PORT"

python3 -m http.server $PORT --directory dist &
SERVER_PID=$!

trap "kill $SERVER_PID 2>/dev/null" EXIT INT TERM

sleep 0.5

if command -v open &>/dev/null; then
    open "$URL"
elif command -v xdg-open &>/dev/null; then
    xdg-open "$URL"
fi

wait $SERVER_PID
