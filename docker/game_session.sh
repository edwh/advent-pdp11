#!/bin/bash
#
# ADVENT MUD Game Session Script
#
# This script runs the game login expect script and handles restarts
# for session takeover functionality.
#
# Exit codes from game_connect.exp:
#   0 = Normal exit
#   1 = Error (don't retry)
#   2 = Kicked (session takeover) - should retry connection
#

EXPECT_SCRIPT="/opt/advent/game_connect.exp"

echo ""
echo "============================================="
echo "    ADVENT MUD - 1987 Multi-User Dungeon"
echo "    Running on RSTS/E V10.1"
echo "============================================="
echo ""

# Configure terminal to not send LF after CR
# RSTS/E only expects CR, and treats LF as an empty command (producing "?" prompts)
stty -icrnl -onlcr -inlcr igncr 2>/dev/null || true

# Retry loop for session takeover
MAX_RETRIES=3
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "Connecting to the PDP-11..."
    echo ""

    # Run the expect script
    "$EXPECT_SCRIPT"
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        # Normal exit - user disconnected
        echo ""
        echo "Session ended."
        exit 0
    elif [ $EXIT_CODE -eq 1 ]; then
        # Explicit error - don't retry
        echo ""
        echo "Connection failed."
        exit 1
    elif [ $EXIT_CODE -eq 2 ] || [ $EXIT_CODE -gt 128 ]; then
        # Exit code 2 = kicked for takeover
        # Exit code >128 = killed by signal (e.g., from kick_console.sh)
        # Either way, retry the connection
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo ""
        echo "Reconnecting... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
        # Continue loop to retry
    else
        # Other errors - don't retry
        echo ""
        echo "Connection failed (exit code: $EXIT_CODE)"
        exit $EXIT_CODE
    fi
done

echo ""
echo "Failed to connect after $MAX_RETRIES attempts."
exit 1
