#!/bin/bash
#
# Kick existing console connections to allow a new session to take over
#
# This script:
# 1. Creates a signal file that game_connect.exp watches for
# 2. Kills any existing nc processes connected to port 2322
# 3. Kills any ttyd game sessions that might be holding the connection
#

echo "Kicking existing console connections..."

# Signal any waiting game_connect.exp to exit
touch /tmp/kick_console

# Kill existing nc connections to console port
pkill -f 'nc localhost 2322' || true
pkill -f 'nc 127.0.0.1 2322' || true

# Kill game_connect.exp processes (but not this caller's session)
# Find expect processes running game_connect
for pid in $(pgrep -f 'expect.*game_connect'); do
    # Don't kill ourselves or our parent
    if [ "$pid" != "$$" ] && [ "$pid" != "$PPID" ]; then
        kill "$pid" 2>/dev/null || true
    fi
done

# Small delay to let connections close
sleep 1

# Clean up signal file
rm -f /tmp/kick_console

echo "Done. Console should now be available."
