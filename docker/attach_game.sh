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

# Check if the game session exists (screen session named "advent")
if ! screen -list | grep -q "\.advent"; then
    echo "Game session not found. Please wait for the system to start."
    echo '{"step": "error", "message": "Game session not ready - please wait"}' > /tmp/login_status.json
    sleep 5
    exit 1
fi

echo '{"step": "ready", "message": "Game ready!"}' > /tmp/login_status.json
echo "Connecting to ADVENT..."
echo ""

# Configure terminal settings for proper backspace handling
# RSTS/E expects rubout (DEL/0x7f) for character deletion, but we need to
# ensure the terminal is set up correctly
stty erase '^?' 2>/dev/null || true

# Attach to the screen session
# -x allows multiple viewers to attach simultaneously
# This provides proper terminal I/O handling unlike tmux+expect
exec /usr/bin/screen -x advent
