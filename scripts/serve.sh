#!/usr/bin/env bash
# Serves the built site locally for testing before deploying.
# Run after building (e.g. python3 scripts/build.py) to preview the output in the browser.
set -e

# Resolve to repo root so "dist" is found regardless of where the script is invoked from
cd "$(dirname "$0")/.."

PORT=8000
URL="http://localhost:$PORT"

# Start server in background so we can open the browser immediately after
python3 -m http.server $PORT --directory dist &
SERVER_PID=$!

# Kill the server on Ctrl+C, TERM, or normal exit so it doesn't linger as an orphan process
trap "kill $SERVER_PID 2>/dev/null" EXIT INT TERM

# Give the server a moment to start before opening the browser
sleep 0.5

# open is macOS; xdg-open is Linux
if command -v open &>/dev/null; then
    open "$URL"
elif command -v xdg-open &>/dev/null; then
    xdg-open "$URL"
fi

# Block until the server exits (keeps the terminal attached and the trap active)
wait $SERVER_PID
