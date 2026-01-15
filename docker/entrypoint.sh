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

# Function to wait for a port to be completely free (including TIME_WAIT)
wait_for_port_free() {
    local port=$1
    local max_wait=${2:-30}
    local waited=0
    while [ $waited -lt $max_wait ]; do
        # Check ALL socket states, not just LISTEN (TIME_WAIT also blocks bind)
        if ! ss -an 2>/dev/null | grep -q ":$port "; then
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
    done
    echo "WARNING: Port $port still in use after ${max_wait}s"
    return 1
}

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

# Restore disk image from backup on each start
# This prevents corruption from improper shutdowns
BACKUP_DIR="$ADVENT_DIR/disks-backup"
if [ -f "$BACKUP_DIR/rstse_10_ra72.dsk" ]; then
    echo "Restoring fresh RA72 disk image from backup..."
    cp "$BACKUP_DIR/rstse_10_ra72.dsk" "$DISKS_DIR/rstse_10_ra72.dsk"
    echo "Disk image restored."
fi

# Check for required disk image
if [ ! -f "$DISKS_DIR/rstse_10_ra72.dsk" ]; then
    echo "ERROR: RA72 disk not found at $DISKS_DIR/rstse_10_ra72.dsk"
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

# Start the restart service (listens on port 8081, kills SIMH when called)
"$ADVENT_DIR/restart_service.sh" &
echo "Restart service started on port 8081"

# Start the kick service (listens on port 8082, kicks console connections)
"$ADVENT_DIR/kick_service.sh" &
echo "Kick service started on port 8082"

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

# Wait for RSTS/E to finish booting (event-driven, not fixed sleep)
# We use verify_ready.exp which connects with tcp_connect.py (sends RST on close,
# preventing CLOSE_WAIT issues) and checks for User: prompt
echo "Waiting for RSTS/E to be ready for logins..."
MAX_READY_WAIT=120
READY_WAIT=0
while [ $READY_WAIT -lt $MAX_READY_WAIT ]; do
    if "$ADVENT_DIR/verify_ready.exp" 2>/dev/null; then
        echo "RSTS/E is ready for logins!"
        break
    fi
    echo -n "."
    sleep 5
    READY_WAIT=$((READY_WAIT + 5))
done

if [ $READY_WAIT -ge $MAX_READY_WAIT ]; then
    echo ""
    echo "WARNING: RSTS/E may not be fully ready after $MAX_READY_WAIT seconds"
    echo "Continuing anyway..."
fi

# Run setup (build from source) BEFORE starting web terminals
# This prevents users from connecting while build is in progress
if [ "${SKIP_SETUP:-0}" != "1" ]; then
    echo ""
    echo "=============================================="
    echo "  Running ADVENT Setup"
    echo "=============================================="
    echo ""

    # Update boot status to show build is in progress
    echo '{"status": "building", "message": "Building ADVENT from source...", "detail": "Copying files from tape and compiling. This takes 10-15 minutes.", "progress": "Started"}' > /tmp/boot_status.json

    # Run build_advent.exp to copy from tape and compile
    # This uses TMSCP tape (MU0:) at 18KB/sec - much faster than TECO
    TIMEOUT="${SETUP_TIMEOUT:-7200}"
    timeout $TIMEOUT "$ADVENT_DIR/build_advent.exp" 2>&1 | tee /tmp/setup.log || {
        echo ""
        echo "WARNING: Build completed with errors or timed out."
        echo "Check /tmp/setup.log for details."
        echo ""
    }

    # Kill any lingering connections from build
    # Note: tcp_connect.py sends RST on close, so we shouldn't have CLOSE_WAIT issues
    # anymore, but kill any stray processes just in case
    echo "Cleaning up build connections..."
    pkill -9 -f 'tcp_connect.py.*2322' 2>/dev/null || true
    pkill -9 -f 'telnet localhost 2322' 2>/dev/null || true

    # Restart SIMH to ensure clean state for user connections
    echo "Restarting SIMH for clean state..."
    echo '{"status": "booting", "message": "Restarting emulator..."}' > /tmp/boot_status.json
    pkill -9 pdp11 2>/dev/null || true

    # Wait for SIMH ports to be released (avoid "Address already in use")
    # TIME_WAIT can last up to 60s, so wait longer for the console port
    echo "Waiting for ports to be released..."
    wait_for_port_free 2322 65 || true
    wait_for_port_free 2323 10 || true
    wait_for_port_free 2325 10 || true

    /usr/local/bin/pdp11 "$ADVENT_DIR/pdp11.ini" &
    SIMH_PID=$!
    echo "SIMH restarted (PID: $SIMH_PID)"

    # Verify console port is listening (critical for game connections)
    sleep 2
    if ! ss -tlnp 2>/dev/null | grep -q ":2322 "; then
        echo "WARNING: Console port 2322 not listening - SIMH may have failed to bind"
        echo "Attempting SIMH restart..."
        pkill -9 pdp11 2>/dev/null || true
        wait_for_port_free 2322 65 || true
        /usr/local/bin/pdp11 "$ADVENT_DIR/pdp11.ini" &
        SIMH_PID=$!
        echo "SIMH restarted again (PID: $SIMH_PID)"
    fi

    # Wait for RSTS/E to reboot (event-driven)
    echo "Waiting for RSTS/E to reboot..."
    echo '{"status": "booting", "message": "Waiting for RSTS/E to reboot..."}' > /tmp/boot_status.json
    MAX_REBOOT_WAIT=120
    REBOOT_WAIT=0
    while [ $REBOOT_WAIT -lt $MAX_REBOOT_WAIT ]; do
        if "$ADVENT_DIR/verify_ready.exp" 2>/dev/null; then
            echo "RSTS/E is ready after reboot!"
            break
        fi
        echo -n "."
        sleep 5
        REBOOT_WAIT=$((REBOOT_WAIT + 5))
    done

    if [ $REBOOT_WAIT -ge $MAX_REBOOT_WAIT ]; then
        echo ""
        echo "WARNING: RSTS/E may not be fully ready after reboot"
    fi

    # Update status after build completes
    echo '{"status": "booting", "message": "Build complete, starting game session..."}' > /tmp/boot_status.json
fi

# Start persistent game session in tmux
# This logs in once and keeps ADVENT running - users attach to this session
echo "Starting persistent ADVENT game session..."
echo '{"status": "booting", "message": "Starting ADVENT game session..."}' > /tmp/boot_status.json

# Kill any existing tmux sessions
tmux kill-session -t advent 2>/dev/null || true

# Start game session in detached tmux
tmux new-session -d -s advent "expect -f $ADVENT_DIR/start_game_session.exp"

# Wait for game session to be ready
echo "Waiting for game session to start..."
GAME_WAIT=0
MAX_GAME_WAIT=60
while [ $GAME_WAIT -lt $MAX_GAME_WAIT ]; do
    if tmux has-session -t advent 2>/dev/null; then
        sleep 3
        echo "Game session started!"
        break
    fi
    sleep 2
    GAME_WAIT=$((GAME_WAIT + 2))
done

if [ $GAME_WAIT -ge $MAX_GAME_WAIT ]; then
    echo "WARNING: Game session may not have started properly"
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
echo ""
echo "The game is already running - just connect via the web interface!"
echo ""

# Note: nginx started at beginning of boot for health checks

# Start ttyd web terminals - users attach to the persistent screen session
ttyd -p 7681 -b /terminal -W "$ADVENT_DIR/attach_game.sh" &
GAME_PID=$!
echo "Game web terminal started on port 7681"

ttyd -p 7682 -W "$ADVENT_DIR/admin_connect.sh" &
ADMIN_PID=$!
echo "Admin web terminal started on port 7682"

# Mark system as ready
echo '{"status": "ready", "message": "System ready"}' > /tmp/boot_status.json

# Wait for the initial SIMH to exit, then restart in a loop
# This keeps the container running and allows restarts
# Note: wait returns non-zero when process is killed, so we ignore the exit status
wait $SIMH_PID || true

# Run SIMH in a loop - if it exits (or is killed for restart), restart it
while true; do
    echo ""
    echo "SIMH exited. Restarting in 3 seconds..."
    echo '{"status": "booting", "message": "Restarting PDP-11..."}' > /tmp/boot_status.json
    rm -f /tmp/login_status.json

    # Kill ttyd processes to free the console port for verification
    pkill -f 'ttyd.*game_session' || true
    pkill -f 'ttyd.*admin_connect' || true

    # Wait for SIMH ports to be released (avoid "Address already in use")
    # TIME_WAIT can last up to 60s, so wait longer for the console port
    echo "Waiting for ports to be released..."
    wait_for_port_free 2322 65 || true
    wait_for_port_free 2323 10 || true
    wait_for_port_free 2325 10 || true

    echo "Starting SIMH emulator..."
    /usr/local/bin/pdp11 "$ADVENT_DIR/pdp11.ini" &
    SIMH_PID=$!

    # Verify console port is listening (critical for game connections)
    sleep 2
    if ! ss -tlnp 2>/dev/null | grep -q ":2322 "; then
        echo "WARNING: Console port 2322 not listening - SIMH may have failed to bind"
        echo "Attempting SIMH restart..."
        pkill -9 pdp11 2>/dev/null || true
        wait_for_port_free 2322 65 || true
        /usr/local/bin/pdp11 "$ADVENT_DIR/pdp11.ini" &
        SIMH_PID=$!
        echo "SIMH restarted again (PID: $SIMH_PID)"
    fi

    # Wait for RSTS/E to boot (event-driven)
    echo "Waiting for RSTS/E to boot..."
    echo '{"status": "booting", "message": "Waiting for RSTS/E..."}' > /tmp/boot_status.json
    MAX_RESTART_WAIT=120
    RESTART_WAIT=0
    while [ $RESTART_WAIT -lt $MAX_RESTART_WAIT ]; do
        if "$ADVENT_DIR/verify_ready.exp" 2>/dev/null; then
            echo "RSTS/E is ready!"
            break
        fi
        echo -n "."
        sleep 5
        RESTART_WAIT=$((RESTART_WAIT + 5))
    done

    if [ $RESTART_WAIT -ge $MAX_RESTART_WAIT ]; then
        echo ""
        echo "WARNING: RSTS/E may not be fully ready"
    fi

    # Restart persistent game session in tmux
    echo "Starting persistent ADVENT game session..."
    echo '{"status": "booting", "message": "Starting ADVENT game session..."}' > /tmp/boot_status.json
    tmux kill-session -t advent 2>/dev/null || true
    tmux new-session -d -s advent "expect -f $ADVENT_DIR/start_game_session.exp"
    sleep 5
    echo "Game session restarted"

    # Restart ttyd processes
    ttyd -p 7681 -b /terminal -W "$ADVENT_DIR/attach_game.sh" &
    GAME_PID=$!
    echo "Game web terminal restarted on port 7681"

    ttyd -p 7682 -W "$ADVENT_DIR/admin_connect.sh" &
    ADMIN_PID=$!
    echo "Admin web terminal restarted on port 7682"

    echo '{"status": "ready", "message": "System ready"}' > /tmp/boot_status.json

    # Wait for SIMH to exit (ignore exit status when killed)
    wait $SIMH_PID || true
done
