#!/usr/bin/env python3
"""
Upload a BASIC program to RSTS/E using the CREATE command.
"""

import socket
import sys
import time

def upload_basic(host: str, port: int, local_file: str, remote_name: str):
    """Upload a BASIC program to RSTS/E."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)

    try:
        print(f"Connecting to {host}:{port}...")
        sock.connect((host, port))

        def send(data: str):
            sock.send((data + "\r").encode('ascii'))
            time.sleep(0.2)

        def recv(timeout: float = 2.0) -> str:
            sock.settimeout(timeout)
            try:
                data = sock.recv(4096).decode('ascii', errors='replace')
                return data
            except socket.timeout:
                return ""

        # Login sequence
        print("Logging in...")
        time.sleep(3)
        send("")
        time.sleep(2)

        data = recv(5)
        if "User:" in data:
            send("[1,2]")
            time.sleep(1)
            recv()
            send("Digital1977")
            time.sleep(2)

            data = recv(3)
            while "Job number" in data:
                send("")
                time.sleep(2)
                data = recv(3)

        # Read local file
        print(f"Reading {local_file}...")
        with open(local_file, 'r') as f:
            lines = f.readlines()

        print(f"Creating {remote_name} with {len(lines)} lines...")
        send(f"CREATE {remote_name}")
        time.sleep(1)
        data = recv()
        print(f"CREATE: {data[:80]}")

        # Handle replace prompt
        if "replace" in data.lower():
            print("  Confirming replace...")
            send("Y")
            time.sleep(0.5)
            data = recv()
            print(f"  After Y: {data[:50]}")

        # Send each line
        for i, line in enumerate(lines):
            line = line.rstrip('\r\n')
            send(line)
            time.sleep(0.05)
            if (i + 1) % 10 == 0:
                print(f"  Sent {i+1}/{len(lines)} lines...")
                # Drain any echo
                recv(0.1)

        # End with Ctrl+Z
        print("Sending Ctrl+Z...")
        sock.send(b"\x1a\r")
        time.sleep(1)
        data = recv()
        print(f"Response: {data[:100]}")

        print("Done!")

    finally:
        sock.close()

def main():
    if len(sys.argv) < 5:
        print("Usage: upload_basic.py <host> <port> <local_file> <remote_name>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    local_file = sys.argv[3]
    remote_name = sys.argv[4]

    upload_basic(host, port, local_file, remote_name)

if __name__ == '__main__':
    main()
