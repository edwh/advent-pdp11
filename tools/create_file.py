#!/usr/bin/env python3
"""
Create a file on RSTS/E using the CREATE command.
Sends Ctrl+Z (0x1A) as end-of-file marker.
"""

import socket
import sys
import time

def create_file(host: str, port: int, filename: str, content: str):
    """Create a file on RSTS/E using CREATE command."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)

    try:
        print(f"Connecting to {host}:{port}...")
        sock.connect((host, port))

        def send(data: str, raw: bool = False):
            if raw:
                sock.send(data.encode('ascii'))
            else:
                sock.send((data + "\r").encode('ascii'))
            time.sleep(0.3)

        def recv(timeout: float = 2.0) -> str:
            sock.settimeout(timeout)
            try:
                data = sock.recv(4096).decode('ascii', errors='replace')
                return data
            except socket.timeout:
                return ""

        # Login sequence
        print("Waiting for login prompt...")
        time.sleep(3)
        send("")  # Wake up
        time.sleep(2)

        data = recv(5)
        if "User:" in data:
            print("Logging in as [1,2]...")
            send("[1,2]")
            time.sleep(1)
            recv()
            send("Digital1977")
            time.sleep(2)

            # Handle detached jobs prompt
            data = recv(3)
            while "Job number" in data:
                send("")
                time.sleep(2)
                data = recv(3)

        print(f"Creating file: {filename}")
        send(f"CREATE {filename}")
        time.sleep(1)
        data = recv()
        print(f"CREATE response: {data[:100]}")

        # Handle "OK to replace" prompt
        if "replace" in data.lower():
            print("File exists, confirming replace...")
            send("Y")
            time.sleep(0.5)
            data = recv()
            print(f"After Y: {data[:100]}")

        # Send content line by line
        for line in content.split('\n'):
            print(f"Sending: {line}")
            send(line)
            time.sleep(0.2)

        # Send Ctrl+Z to end the file
        print("Sending Ctrl+Z to end file...")
        sock.send(b"\x1a\r")  # Ctrl+Z + CR
        time.sleep(1)
        data = recv()
        print(f"After Ctrl+Z: {data[:200]}")

        # Also try CR after Ctrl+Z
        send("")
        time.sleep(1)
        data = recv()
        print(f"Final response: {data[:200]}")

        print("Done!")

    finally:
        sock.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: create_file.py <host> <port> <filename> [content]")
        print("If content not specified, reads from stdin")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    filename = sys.argv[3]

    if len(sys.argv) > 4:
        content = sys.argv[4]
    else:
        content = sys.stdin.read()

    create_file(host, port, filename, content)

if __name__ == '__main__':
    main()
