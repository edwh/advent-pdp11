#!/bin/bash
#
# ADVENT MUD Docker Entrypoint
#
# This script orchestrates the complete startup of ADVENT MUD:
# 1. Generate data files from salvaged sources
# 2. Start SIMH with RSTS/E
# 3. Wait for RSTS/E to boot
# 4. Transfer data files
# 5. Transfer source files
# 6. Compile and link (optional)
# 7. Start web terminals
#
# Environment variables:
#   SKIP_SETUP=1       - Skip file transfer and compilation (use pre-built disk)
#   SKIP_DATA=1        - Skip data file transfer
#   SKIP_SOURCE=1      - Skip source file transfer
#   SKIP_COMPILE=1     - Skip compilation and linking
#   SETUP_TIMEOUT=7200 - Timeout for setup in seconds (default 2 hours)
#

set -e

echo "=============================================="
echo "  Advent MUD - 1987 Multi-User Dungeon"
echo "  Running on SIMH PDP-11 / RSTS/E V10.1"
echo "=============================================="
echo

# Clear any stale status from previous runs
rm -f /tmp/login_status.json
rm -f /tmp/boot_ready.json

# Write initial boot status (system starting)
echo '{"status": "booting", "message": "Starting PDP-11 emulator..."}' > /tmp/boot_status.json

# Configuration
ADVENT_DIR="/opt/advent"
DISKS_DIR="$ADVENT_DIR/disks"
DATA_DIR="$ADVENT_DIR/data"
SRC_DIR="$ADVENT_DIR/src"
SCRIPTS_DIR="$ADVENT_DIR/scripts"

# Check for required disk images
if [ ! -f "$DISKS_DIR/rsts0.dsk" ]; then
    echo "ERROR: Boot disk not found at $DISKS_DIR/rsts0.dsk"
    exit 1
fi

if [ ! -f "$DISKS_DIR/rsts1.dsk" ]; then
    echo "ERROR: Game disk not found at $DISKS_DIR/rsts1.dsk"
    exit 1
fi

# Generate data files if salvage sources exist and data files don't
if [ -f "$DATA_DIR/roomfil.fil" ] && [ ! -f "$DATA_DIR/ADVENT.DTA" ]; then
    echo "Generating data files from salvaged sources..."
    python3 "$SCRIPTS_DIR/migrate_data.py" --data-dir "$DATA_DIR" --output-dir "$DATA_DIR" 2>&1 || true
fi

# Start nginx early so health checks pass during boot
# The web interface will show "booting" status until RSTS/E is ready
if command -v nginx &> /dev/null; then
    nginx
    echo "Web interface started on port 8080 (serving boot status)"
fi

# Start SIMH in background
echo "Starting SIMH emulator..."
echo "  Console: telnet localhost 2322"
echo "  Terminals: telnet localhost 2323"
echo

/usr/local/bin/pdp11 "$ADVENT_DIR/pdp11.ini" &
SIMH_PID=$!

# Wait for SIMH to start
sleep 3
if ! kill -0 $SIMH_PID 2>/dev/null; then
    echo "ERROR: SIMH failed to start"
    echo '{"status": "error", "message": "SIMH failed to start"}' > /tmp/boot_status.json
    exit 1
fi
echo "SIMH started (PID: $SIMH_PID)"

# Update boot status
echo '{"status": "booting", "message": "Waiting for RSTS/E to boot (this takes ~5 minutes)..."}' > /tmp/boot_status.json

# Wait for RSTS/E to boot (check if port 2323 is accepting connections)
echo "Waiting for RSTS/E to boot..."
MAX_BOOT_WAIT=120
BOOT_WAIT=0
while [ $BOOT_WAIT -lt $MAX_BOOT_WAIT ]; do
    if nc -z localhost 2323 2>/dev/null; then
        echo "RSTS/E terminal port is ready!"
        break
    fi
    echo -n "."
    sleep 2
    BOOT_WAIT=$((BOOT_WAIT + 2))
done

if [ $BOOT_WAIT -ge $MAX_BOOT_WAIT ]; then
    echo ""
    echo "ERROR: RSTS/E did not respond within $MAX_BOOT_WAIT seconds"
    echo '{"status": "error", "message": "RSTS/E boot timeout"}' > /tmp/boot_status.json
    exit 1
fi

# Update boot status - waiting for full initialization
echo '{"status": "booting", "message": "RSTS/E initializing services..."}' > /tmp/boot_status.json

# Actively verify RSTS/E is ready for terminal logins
# Instead of a blind wait, we actually try to get a User: prompt
echo "Verifying RSTS/E terminal readiness..."
MAX_READY_WAIT=600  # 10 minutes max
READY_WAIT=0
while [ $READY_WAIT -lt $MAX_READY_WAIT ]; do
    if "$ADVENT_DIR/verify_ready.exp" 2>/dev/null; then
        echo "RSTS/E terminals are ready for login!"
        break
    fi
    echo -n "."
    sleep 10
    READY_WAIT=$((READY_WAIT + 10))
done

if [ $READY_WAIT -ge $MAX_READY_WAIT ]; then
    echo ""
    echo "WARNING: RSTS/E may not be fully ready after $MAX_READY_WAIT seconds"
    echo "Continuing anyway..."
fi

# Start web terminals BEFORE marking system ready
# This ensures ttyd is running when users try to connect
if command -v ttyd &> /dev/null; then
    # Game interface (port 7681) - auto-login and run ADVENT (proxied via nginx)
    # -b /terminal tells ttyd it's being proxied at /terminal/ path
    ttyd -p 7681 -b /terminal -W "$ADVENT_DIR/game_session.sh" &
    GAME_PID=$!
    echo "Game web terminal started on port 7681"

    # Admin interface (port 7682) - direct console access
    ttyd -p 7682 -W "$ADVENT_DIR/admin_connect.sh" &
    ADMIN_PID=$!
    echo "Admin web terminal started on port 7682"

    # Give ttyd a moment to start
    sleep 2
fi

# Mark system as ready
echo '{"status": "ready", "message": "System ready"}' > /tmp/boot_status.json

# Run setup if not skipped
if [ "${SKIP_SETUP:-0}" != "1" ]; then
    echo ""
    echo "=============================================="
    echo "  Running ADVENT Setup"
    echo "=============================================="
    echo ""

    SETUP_ARGS=""
    [ "${SKIP_DATA:-0}" = "1" ] && SETUP_ARGS="$SETUP_ARGS --skip-data"
    [ "${SKIP_SOURCE:-0}" = "1" ] && SETUP_ARGS="$SETUP_ARGS --skip-source"
    [ "${SKIP_COMPILE:-0}" = "1" ] && SETUP_ARGS="$SETUP_ARGS --skip-compile"

    # Run setup with timeout
    TIMEOUT="${SETUP_TIMEOUT:-7200}"
    timeout $TIMEOUT python3 "$SCRIPTS_DIR/setup_advent.py" \
        --data-dir "$DATA_DIR" \
        --source-dir "$SRC_DIR" \
        $SETUP_ARGS 2>&1 | tee /tmp/setup.log || {
        echo ""
        echo "WARNING: Setup completed with errors or timed out."
        echo "Check /tmp/setup.log for details."
        echo ""
    }
fi

echo ""
echo "=============================================="
echo "  System Ready"
echo "=============================================="
echo ""
echo "Access methods:"
echo "  CRT Web Interface:    http://localhost:8080"
echo "  Web Terminal (Admin): http://localhost:7682"
echo "  Telnet (Console):     telnet localhost 2322"
echo "  Telnet (Terminal):    telnet localhost 2323"
echo ""
echo "To login via telnet:"
echo "  User: [1,2]"
echo "  Password: Digital1977"
echo ""
echo "To run the game after login:"
echo "  RUN ADVENT"
echo ""

# Note: nginx started at beginning of boot for health checks
# Note: ttyd started before marking system ready

# Keep running - wait for SIMH to exit
wait $SIMH_PID
