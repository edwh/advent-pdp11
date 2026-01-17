#!/bin/bash
#
# Attach user to the persistent ADVENT game session
# This connects to the tmux session started by entrypoint.sh
#

echo "=============================================="
echo "    ADVENT MUD - 1987 Multi-User Dungeon"
echo "    Running on RSTS/E V10.1"
echo "=============================================="
echo ""

# Update status for web UI
echo '{"step": "connect", "message": "Connecting to game session..."}' > /tmp/login_status.json

# Check if the game session exists
if ! tmux has-session -t advent 2>/dev/null; then
    echo "Game session not found. Please wait for the system to start."
    echo '{"step": "error", "message": "Game session not ready - please wait"}' > /tmp/login_status.json
    sleep 5
    exit 1
fi

echo '{"step": "ready", "message": "Game ready!"}' > /tmp/login_status.json
echo "Connecting to ADVENT..."
echo ""

# Attach to the tmux session with status bar hidden
# Use -d to detach any existing clients first - prevents stale connections
# from blocking keyboard input when previous session didn't disconnect cleanly
exec /usr/bin/tmux set-option -t advent status off \; attach-session -d -t advent
