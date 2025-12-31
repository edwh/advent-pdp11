#!/usr/bin/env python3
"""
Run commands on RSTS/E via telnet
"""

import socket
import sys
import time

def run_command(host: str, port: int, command: str):
    """Run a command on RSTS/E."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)

    try:
        print(f"Connecting to {host}:{port}...")
        sock.connect((host, port))

        def send(data: str):
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

        print(f"Running: {command}")
        send(command)
        time.sleep(2)
        data = recv(5)
        print("Output:")
        print(data)

        # Logout
        send("BYE")
        time.sleep(1)

    finally:
        sock.close()

def main():
    if len(sys.argv) < 4:
        print("Usage: rsts_cmd.py <host> <port> <command>")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    command = " ".join(sys.argv[3:])

    run_command(host, port, command)

if __name__ == '__main__':
    main()
