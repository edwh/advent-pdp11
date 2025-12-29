#!/bin/bash
# Advent MUD Startup Script
# Starts SIMH PDP-11 with RSTS/E via web terminal

echo "=============================================="
echo "  Advent MUD - 1987 Multi-User Dungeon"
echo "  Running on SIMH PDP-11 / RSTS/E V7"
echo "=============================================="
echo ""
echo "Web terminal will be available on port 7681"
echo ""
echo "RSTS/E Login Instructions:"
echo "  1. Press Enter at 'Option:' prompt"
echo "  2. Enter date/time when prompted (e.g., 29-DEC-25 12:00)"
echo "  3. Press Enter at 'Command File:' prompt"
echo "  4. Login with: HELLO 1,2"
echo "  5. Password: SYSTEM"
echo ""
echo "Starting emulator..."
echo ""

# Start ttyd with SIMH
exec ttyd -p 7681 -W /usr/local/bin/pdp11 /opt/advent/pdp11.ini
