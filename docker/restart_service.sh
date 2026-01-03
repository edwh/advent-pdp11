#!/bin/bash
# Simple HTTP service that restarts SIMH when called
# Listens on port 8081 and responds to any request by killing pdp11

while true; do
    # Wait for HTTP request on port 8081
    echo -e "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n{\"status\": \"restarting\"}" | nc -l -p 8081 -q 1 > /dev/null 2>&1

    # Kill SIMH - the entrypoint loop will restart it
    echo "Restart requested - killing SIMH..."
    pkill -9 pdp11 2>/dev/null || true

    # Small delay before accepting next request
    sleep 1
done
