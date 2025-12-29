#!/bin/bash
# Advent MUD Startup Script
# Runs SIMH PDP-11 with RSTS/E V10.1 and web terminals

echo "=============================================="
echo "  Advent MUD - 1987 Multi-User Dungeon"
echo "  Running on SIMH PDP-11 / RSTS/E V10.1"
echo "=============================================="
echo ""
echo "Starting SIMH emulator..."

# Start SIMH in background (listens on TCP ports 2322 and 2323)
/usr/src/simh/BIN/pdp11 /opt/advent/pdp11.ini &
SIMH_PID=$!

# Wait for SIMH to open ports
sleep 2

echo "Running autoboot..."
/opt/advent/autoboot.exp &
BOOT_PID=$!

# Wait for boot to complete
wait $BOOT_PID
echo "Autoboot finished."

echo ""
echo "Web interfaces:"
echo "  Port 7681 = Game (connect to Advent)"
echo "  Port 7682 = Admin (RSTS/E console)"
echo ""

# Start game interface (port 7681) - connects to DZ11 terminal
ttyd -p 7681 -W /opt/advent/game_connect.exp &
GAME_PID=$!

# Start admin interface (port 7682) - direct console
ttyd -p 7682 -W /opt/advent/admin_connect.sh &
ADMIN_PID=$!

echo "All services started. RSTS/E is ready."

# Wait for any process to exit
wait -n $SIMH_PID $GAME_PID $ADMIN_PID

# If any exits, kill the others
kill $SIMH_PID $GAME_PID $ADMIN_PID 2>/dev/null
