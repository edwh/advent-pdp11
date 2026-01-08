#!/bin/bash
# Simple HTTP service that kicks existing console connections when called
# Listens on port 8082 and responds to any request by running kick_console.sh

SCRIPT_DIR="$(dirname "$0")"

while true; do
    # Wait for HTTP request on port 8082
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n{\"status\": \"kicked\"}" | nc -l -p 8082 -q 1 > /dev/null 2>&1

    # Run kick script
    echo "Kick requested - terminating existing console connections..."
    "$SCRIPT_DIR/kick_console.sh"

    # Small delay before accepting next request
    sleep 1
done
