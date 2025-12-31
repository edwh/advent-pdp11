#!/usr/bin/env python3
"""
XFER file sender - Send files to RSTS/E via hex-encoded protocol

Usage: xfer_send.py <host> <port> <local_file> <remote_filename>

Protocol:
  :filename     - Start receiving file
  :NNNN:HH...   - Hex data line with line number
  :END          - End of file
"""

import socket
import sys
import time

def hex_encode_line(data: bytes, line_num: int, line_size: int = 32) -> str:
    """Encode bytes as hex with line number and checksum."""
    hex_data = data.hex().upper()
    # Format: :NNNN:HEXDATA:CC (checksum optional for now)
    return f":{line_num:04X}:{hex_data}"

def send_file(host: str, port: int, local_file: str, remote_name: str,
              wait_for_login: bool = True, username: str = "[1,2]", password: str = "Digital1977"):
    """Send a file to RSTS/E via XFER protocol."""

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

        if wait_for_login:
            print("Waiting for login prompt...")
            time.sleep(3)
            send("")  # Wake up
            time.sleep(2)

            data = recv(5)
            if "User:" in data:
                print(f"Logging in as {username}...")
                send(username)
                time.sleep(1)
                recv()
                send(password)
                time.sleep(2)

                # Handle detached jobs prompt
                data = recv(3)
                while "Job number" in data:
                    send("")  # Just press enter
                    time.sleep(2)
                    data = recv(3)

                print("Logged in, starting XFER4...")
                send("RUN XFER4.SAV")
                time.sleep(2)
                data = recv()
                if "V1.0" not in data:
                    print(f"Warning: XFER3 may not have started: {data[:100]}")

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
        if "OK" not in data:
            print(f"Warning: unexpected response: {data[:100]}")

        # Send data in chunks
        line_size = 32  # 32 bytes per line = 64 hex chars
        line_num = 0
        total_sent = 0

        for i in range(0, len(file_data), line_size):
            chunk = file_data[i:i+line_size]
            line = hex_encode_line(chunk, line_num, line_size)
            send(line)
            total_sent += len(chunk)
            line_num += 1

            # Wait for OK
            data = recv(1)
            if "ERR" in data:
                print(f"Error on line {line_num}: {data}")
                break

            if line_num % 10 == 0:
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

        # Exit XFER
        sock.send(b"\x03")  # Ctrl+C
        time.sleep(1)

        print("Done!")

    finally:
        sock.close()

def main():
    if len(sys.argv) < 5:
        print(__doc__)
        print("Example: xfer_send.py localhost 2323 myfile.txt MYFILE.TXT")
        sys.exit(1)

    host = sys.argv[1]
    port = int(sys.argv[2])
    local_file = sys.argv[3]
    remote_name = sys.argv[4]

    send_file(host, port, local_file, remote_name)

if __name__ == '__main__':
    main()
