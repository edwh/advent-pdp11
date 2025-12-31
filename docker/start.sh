#!/bin/sh
# Advent MUD Startup Script
# Runs SIMH PDP-11 with RSTS/E V10.1 and web terminals

set -e

echo "=============================================="
echo "  Advent MUD - 1987 Multi-User Dungeon"
echo "  Running on SIMH PDP-11 / RSTS/E V10.1"
echo "=============================================="
echo

# Verify disk images exist
if [ ! -f /opt/advent/disks/rsts0.dsk ]; then
    echo "ERROR: Boot disk not found!"
    exit 1
fi

if [ ! -f /opt/advent/disks/rsts1.dsk ]; then
    echo "ERROR: Game disk not found!"
    exit 1
fi

echo "Starting SIMH emulator..."
echo "  Console: telnet localhost 2322"
echo "  Terminals: telnet localhost 2323"
echo

# Start SIMH in background
# The pdp11.ini contains auto-boot expect scripts
/usr/src/simh/BIN/pdp11 /opt/advent/pdp11.ini &
SIMH_PID=$!

# Wait for SIMH to start and open ports
sleep 3

# Check if SIMH started
if ! kill -0 $SIMH_PID 2>/dev/null; then
    echo "ERROR: SIMH failed to start"
    exit 1
fi

echo "SIMH started (PID: $SIMH_PID)"

# Wait a bit for RSTS/E to boot
echo "Waiting for RSTS/E to boot..."
sleep 15

echo
echo "=============================================="
echo "  System Ready"
echo "=============================================="
echo
echo "Access methods:"
echo "  Web Terminal (Game):  http://localhost:7681"
echo "  Web Terminal (Admin): http://localhost:7682"
echo "  Telnet (Console):     telnet localhost 2322"
echo "  Telnet (Terminal):    telnet localhost 2323"
echo
echo "To login via telnet:"
echo "  User: [1,2]"
echo "  Password: Digital1977"
echo
echo "To run the game after login:"
echo "  RUN DM1:[1,2]ADVENT"
echo

# Start web terminals if ttyd is available
if command -v ttyd &> /dev/null; then
    # Game interface (port 7681) - connects via netcat to DZ11 terminal
    ttyd -p 7681 -W /opt/advent/game_connect.exp &
    GAME_PID=$!
    echo "Game web terminal started on port 7681"

    # Admin interface (port 7682) - direct console access
    ttyd -p 7682 -W /opt/advent/admin_connect.sh &
    ADMIN_PID=$!
    echo "Admin web terminal started on port 7682"
fi

# Keep running - wait for SIMH to exit
wait $SIMH_PID
