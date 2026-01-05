#!/bin/bash
#
# entrypoint_bootstrap.sh - Bootstrap ADVENT from source on first run
#
# This script:
# 1. Starts SIMH emulator
# 2. Waits for RSTS/E to boot
# 3. Checks if ADVENT needs to be built
# 4. If needed, runs bootstrap to compile from source
# 5. Starts web interface and game connection
#

set -e

cd /opt/advent

# For bootstrap edition, we always build from source on fresh container start
# This ensures the TSK always matches the source code on the tape
# The disk images reset on each container start, so builds don't persist

echo "=============================================="
echo "  ADVENT MUD - Bootstrap Edition"
echo "  Building from source via tape transfer"
echo "=============================================="
echo ""
echo "This container builds ADVENT from source on every start."
echo "First boot takes ~3 minutes for compilation."
echo ""

# Start nginx for web interface
echo "Starting web server..."
nginx

echo ""
echo "Access points:"
echo "  CRT Web Interface:    http://localhost:8080"
echo "  Telnet (Console):     telnet localhost 2322"
echo "  Telnet (Terminal):    telnet localhost 2323"
echo ""
echo "Login credentials:"
echo "  User: [1,2]"
echo "  Password: Digital1977"
echo ""

# Function to start SIMH
start_simh() {
    echo "Starting SIMH emulator..."
    /opt/advent/pdp11 /opt/advent/pdp11.ini &
    SIMH_PID=$!
    echo "SIMH started (PID: $SIMH_PID)"
}

# Function to wait for RSTS/E to be ready (waits for "on the air" message)
wait_for_rsts() {
    echo "Waiting for RSTS/E to boot..."
    local max_wait=300
    local waited=0

    while [ $waited -lt $max_wait ]; do
        # Wait for "on the air" which means boot is complete
        # Use longer timeout per attempt since disk rebuild can take time
        if expect -c '
            set timeout 90
            log_user 0
            spawn nc localhost 2322
            expect {
                "on the air" { exit 0 }
                "startup is complete" { exit 0 }
                "User:" { exit 0 }
                -re {\n\$ } { exit 0 }
                timeout { exit 1 }
                eof { exit 1 }
            }
        ' 2>/dev/null; then
            echo "RSTS/E boot complete!"
            # Give it a moment to finish startup
            sleep 5
            return 0
        fi
        sleep 5
        waited=$((waited + 5))
        echo "  Still waiting... ($waited seconds)"
    done

    echo "ERROR: RSTS/E did not become ready in $max_wait seconds"
    return 1
}

# Function to run bootstrap
run_bootstrap() {
    echo ""
    echo "=============================================="
    echo "  Running bootstrap - Building ADVENT from source"
    echo "=============================================="
    echo ""

    # Give RSTS/E a moment to fully stabilize
    sleep 10

    # Run the bootstrap script
    if /opt/advent/bootstrap_advent.exp; then
        echo "Bootstrap completed successfully!"
        touch "$BOOTSTRAP_DONE"
        return 0
    else
        echo "ERROR: Bootstrap failed!"
        return 1
    fi
}

# Function to check if ADVENT is already built
check_advent_exists() {
    # Try to run a quick check for ADVENT.TSK
    # Must check for "ADVENT.TSK" AND NOT "Can't find"
    expect -c '
        set timeout 30
        log_user 0
        spawn nc localhost 2322
        sleep 2
        send "\r"
        expect {
            "User:" { send "\[1,2\]\r" }
            -re {\$} { }
            timeout { exit 1 }
        }
        expect {
            "Password:" { send "Digital1977\r" }
            -re {\$} { }
        }
        expect {
            "Job number" { send "\r"; exp_continue }
            -re {\$} { }
            timeout { exit 1 }
        }
        send "DIR DM1:ADVENT.TSK\r"
        expect {
            "find" {
                # "Cant find" means not present
                send "BYE\r"
                exit 1
            }
            "ADVENT.TSK" {
                # File exists only if we see the name without "find"
                send "BYE\r"
                exit 0
            }
            -re {\$} {
                # Prompt without seeing file - not found
                send "BYE\r"
                exit 1
            }
            timeout { exit 1 }
        }
    ' 2>/dev/null
    return $?
}

# Track if we've already built in this container session
BUILT_THIS_SESSION=false

# Main loop
while true; do
    start_simh

    if wait_for_rsts; then
        # Build from source on first boot of this container session
        if [ "$BUILT_THIS_SESSION" = false ]; then
            echo ""
            echo "Building ADVENT from source..."
            if run_bootstrap; then
                echo "ADVENT successfully built from source!"
                BUILT_THIS_SESSION=true
            else
                echo "Bootstrap failed - check logs for details"
            fi
        fi

        # Verify ADVENT exists
        sleep 5
        if check_advent_exists; then
            echo ""
            echo "=============================================="
            echo "  ADVENT.TSK verified - system is ready!"
            echo "=============================================="
            echo ""
            echo "Connect via:"
            echo "  Web: http://localhost:8080"
            echo "  Telnet: telnet localhost 2322"
            echo "  Run: RUN DM1:ADVENT"
            echo ""
        else
            echo "Warning: ADVENT.TSK not found"
        fi

        # Wait for SIMH to exit
        wait $SIMH_PID 2>/dev/null || true
    fi

    echo ""
    echo "SIMH exited. Restarting in 5 seconds..."
    sleep 5
done
