#!/bin/bash
# Boot RSTS/E by sending console commands
# Uses netcat to send boot prompts

set -e

echo "Waiting for SIMH console..."
sleep 3

# Connect and send boot prompts - use a here-doc with delays
# The prompts are: date, time, start timesharing, option
{
    sleep 2
    echo ""                     # Wake up
    sleep 3
    echo "1-JAN-92"            # Today's date?
    sleep 2
    echo "12:00"               # Current time?
    sleep 2
    echo "Y"                   # Start timesharing?
    sleep 2
    echo ""                    # Option:
    sleep 2
} | nc -q 5 localhost 2322

echo "Boot commands sent to RSTS/E console"
exit 0
