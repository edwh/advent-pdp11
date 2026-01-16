#!/bin/bash
#
# Simple game session using shell and telnet
# This avoids expect's interact issues with tmux
#

echo ">>> Starting persistent game session..."

# Create a fifo for bidirectional communication
FIFO=/tmp/advent_fifo
rm -f $FIFO
mkfifo $FIFO

# Function to send a command and wait
send_and_wait() {
    local cmd="$1"
    local wait_for="$2"
    local timeout="${3:-30}"

    echo "$cmd" >&3
    sleep 0.5
}

# Start telnet in background, reading from fifo
exec 3<>$FIFO
(
    # Wait for User prompt, login, start game
    sleep 5  # Wait for boot messages
    echo ""  # Send CR to get prompt
    sleep 2
    echo "1,2"  # Username
    sleep 1
    echo "SYSTEM"  # Password
    sleep 2
    echo ""  # Accept job
    sleep 2
    echo "RUN ADVENT"  # Start game
    sleep 3
    # Keep fifo open
    cat
) | telnet localhost 2322 2>&1 | tee /tmp/advent_session.log &
TELNET_PID=$!

# Wait for game to start
sleep 15

echo ">>> Persistent game session is ready"
echo ">>> Users can now attach to this session"

# Keep the session alive - just wait for telnet to exit
wait $TELNET_PID
