#!/bin/bash
#
# Start persistent ADVENT game session using screen
#
# This script:
# 1. Creates a screen session with telnet to RSTS/E console
# 2. Sends login commands via screen's stuff command
# 3. Starts ADVENT
#
# Users then attach via: screen -x advent
#
# Using screen instead of tmux+expect because:
# - screen's stuff command reliably sends input to detached sessions
# - screen -x allows multiple simultaneous viewers with proper I/O
# - No expect interact issues in detached mode
#

set -e

MAX_RETRIES=5
RETRY_COUNT=0
CONNECTED=0

echo ">>> Starting persistent game session with screen..."

# Kill any existing screen session
screen -S advent -X quit 2>/dev/null || true
sleep 1

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ $CONNECTED -eq 0 ]; do
    echo ">>> Connection attempt $((RETRY_COUNT + 1))/$MAX_RETRIES..."

    # Create detached screen session with telnet
    # Set terminal size to 80x24 (authentic VT100 dimensions)
    screen -dmS advent bash -c "stty cols 80 rows 24; exec telnet localhost 2322"

    # Wait for connection
    sleep 3

    # Check if screen session exists
    if ! screen -list | grep -q "advent"; then
        echo ">>> Screen session failed to start"
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep 5
        continue
    fi

    # Wait for boot messages and User: prompt
    # Send a CR to wake up the console if needed
    echo ">>> Waiting for login prompt..."
    sleep 2
    screen -S advent -X stuff "\r"
    sleep 3

    # Check if we can interact (session still alive)
    if screen -list | grep -q "advent"; then
        echo ">>> Screen session active, proceeding with login"
        CONNECTED=1
    else
        echo ">>> Connection lost, retrying..."
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep 5
    fi
done

if [ $CONNECTED -eq 0 ]; then
    echo ">>> Failed to connect after $MAX_RETRIES attempts"
    exit 1
fi

# Function to send text with delay between characters
# Usage: slow_stuff "text"
slow_stuff() {
    local text="$1"
    for ((i=0; i<${#text}; i++)); do
        char="${text:$i:1}"
        screen -S advent -X stuff "$char"
        sleep 0.05
    done
}

# Function to send a line (with CR)
send_line() {
    local text="$1"
    slow_stuff "$text"
    screen -S advent -X stuff "\r"
}

# Login sequence
echo ">>> Logging in as 1,2..."
send_line "1,2"
sleep 2

echo ">>> Sending password..."
send_line "SYSTEM"
sleep 2

# Handle job attachment prompt (just press enter)
echo ">>> Handling prompts..."
screen -S advent -X stuff "\r"
sleep 2

# Start ADVENT
echo ">>> Starting ADVENT..."
send_line "RUN ADVENT"
sleep 3

echo ">>> Persistent game session is ready"
echo ">>> Users can now attach with: screen -x advent"

# Keep this script running so entrypoint.sh knows the session is active
# The actual game runs in the screen session
while screen -list | grep -q "advent"; do
    sleep 10
done

echo ">>> Screen session ended"
