#!/usr/bin/env python3
"""
Send files to RSTS/E via BASIC HEXRECV program.
"""

import socket
import sys
import time

def hex_encode_line(data: bytes, line_num: int) -> str:
    """Encode bytes as hex with line number."""
    hex_data = data.hex().upper()
    return f":{line_num:04X}:{hex_data}"

def send_file(host: str, port: int, local_file: str, remote_name: str):
    """Send a file to RSTS/E via BASIC HEXRECV."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)

    try:
        print(f"Connecting to {host}:{port}...")
        sock.connect((host, port))

        def send(data: str):
            sock.send((data + "\r").encode('ascii'))
            time.sleep(0.15)

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

        # Start BASIC and load HEXRECV
        print("Starting BASIC...")
        send("BASIC")
        time.sleep(2)
        data = recv()
        print(f"BASIC: {data[-80:]}")

        print("Loading HEXREC...")
        send("OLD SY:[1,2]HEXREC.BAS")
        time.sleep(1)
        data = recv()
        print(f"OLD: {data}")

        print("Running HEXRECV...")
        send("RUN")
        time.sleep(1)
        data = recv()
        print(f"RUN: {data}")

        if "HEXRECV V1.0" not in data:
            print("Warning: HEXRECV may not have started properly")

        # Read local file
        print(f"Reading {local_file}...")
        with open(local_file, 'rb') as f:
            file_data = f.read()

        print(f"File size: {len(file_data)} bytes")

        # Send filename
        print(f"Sending filename: {remote_name}")
        send(f":{remote_name}")
        time.sleep(0.5)
        data = recv()
        if "ERR" in data:
            print(f"Error: {data}")
            return
        print(f"Response: {data[-40:]}")

        # Send data in chunks
        line_size = 32  # 32 bytes per line
        line_num = 0
        total_sent = 0

        for i in range(0, len(file_data), line_size):
            chunk = file_data[i:i+line_size]
            line = hex_encode_line(chunk, line_num)
            send(line)
            total_sent += len(chunk)
            line_num += 1

            # Read OK response
            data = recv(0.5)
            if "ERR" in data:
                print(f"Error on line {line_num}: {data}")
                break

            if line_num % 20 == 0:
                print(f"  Sent {total_sent}/{len(file_data)} bytes ({100*total_sent//len(file_data)}%)")

        # Send END
        print("Sending END...")
        send(":END")
        time.sleep(1)
        data = recv()

        if "DONE:" in data:
            print(f"Transfer complete! {data}")
        else:
            print(f"Final response: {data}")

        # Exit BASIC
        print("Exiting BASIC...")
        send("BYE")
        time.sleep(1)

        print("Done!")

    finally:
        sock.close()

def main():
    if len(sys.argv) < 5:
        print("Usage: basic_send.py <host> <port> <local_file> <remote_filename>")
        print("Example: basic_send.py localhost 2323 myfile.bin DATA.BIN")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    local_file = sys.argv[3]
    remote_name = sys.argv[4]

    send_file(host, port, local_file, remote_name)

if __name__ == '__main__':
    main()
