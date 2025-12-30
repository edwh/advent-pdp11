#!/usr/bin/env python3
"""
TECO Binary File Transfer for RSTS/E

Transfers binary files to RSTS/E by using TECO's nI command to insert
characters by ASCII code. This method creates files that persist across
RSTS/E restarts (unlike FLX which has block offset issues).

Usage:
    python3 teco_transfer.py <local_file> <remote_filename>

Example:
    python3 teco_transfer.py build/data/ADVENT.DTA ADVENT.DTA
"""

import socket
import time
import sys
import os

# Connection settings
HOST = 'localhost'
PORT = 2323
USER = '[1,2]'
PASSWORD = 'Digital1977'

# TECO escape sequence
ESC_ESC = b'\x1b\x1b'

# Batch size - number of complete nI$$ commands to send at once
# Each command is ~5-6 bytes, so 100 commands = ~600 bytes
# Larger = faster but risks buffer overflow
BATCH_SIZE = 100

def recv_all(sock, timeout=2):
    """Receive all available data with timeout."""
    sock.settimeout(timeout)
    data = b""
    try:
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
    except socket.timeout:
        pass
    return data.decode('latin-1')

def wait_for(sock, pattern, timeout=30, echo=True):
    """Wait for a pattern to appear in the response."""
    sock.settimeout(1)
    data = ""
    start = time.time()
    while time.time() - start < timeout:
        try:
            chunk = sock.recv(4096).decode('latin-1')
            data += chunk
            if echo:
                print(chunk, end='', flush=True)
            if pattern in data:
                return data
        except socket.timeout:
            pass
    return data

def login(sock):
    """Login to RSTS/E."""
    sock.send(b"\r")
    time.sleep(1)
    wait_for(sock, "User:", 10)
    sock.send(f"{USER}\r".encode())
    wait_for(sock, "Password:", 10)
    sock.send(f"{PASSWORD}\r".encode())
    time.sleep(2)
    resp = wait_for(sock, "$", 10)

    # Handle detached job prompt
    if "Job number" in resp:
        sock.send(b"\r")
        wait_for(sock, "$", 10)

def transfer_file(local_path, remote_name):
    """Transfer a binary file to RSTS/E using TECO."""

    # Read the local file
    print(f"Reading {local_path}...")
    with open(local_path, 'rb') as f:
        data = f.read()

    file_size = len(data)
    print(f"File size: {file_size} bytes")

    # Estimate transfer time (very rough)
    # Each byte needs ~4 chars on average ("nI" where n is 1-3 digits)
    # Plus batching overhead
    est_seconds = file_size / 500  # ~500 bytes/sec after overhead
    print(f"Estimated transfer time: {est_seconds/60:.1f} minutes")

    # Connect
    print(f"\nConnecting to {HOST}:{PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    time.sleep(2)

    print("Logging in...")
    login(sock)

    # Delete any existing file with same name
    print(f"\nDeleting existing {remote_name} if present...")
    sock.send(f"DELETE {remote_name}\r".encode())
    time.sleep(1)
    recv_all(sock, 1)

    # Start TECO
    print("Starting TECO...")
    sock.send(b"TECO\r")
    time.sleep(1)
    wait_for(sock, "*", 5, echo=False)

    # Open output file
    print(f"Opening {remote_name} for writing...")
    sock.send(f"EW{remote_name}".encode() + ESC_ESC)
    time.sleep(0.5)
    recv_all(sock, 0.5)

    # Transfer data in batches
    # Each byte becomes "nI$$" where n is the ASCII code and $$ is ESC ESC
    print(f"\nTransferring {file_size} bytes...")
    start_time = time.time()
    last_report = 0

    batch = []
    for i, byte_val in enumerate(data):
        # Add byte as complete "nI$$" command
        batch.append(f"{byte_val}I\x1b\x1b")

        # Send batch when full
        if len(batch) >= BATCH_SIZE:
            cmd = ''.join(batch).encode()
            sock.send(cmd)
            batch = []

            # Small delay to prevent buffer overflow
            time.sleep(0.02)

            # Drain any response
            try:
                sock.settimeout(0.01)
                sock.recv(4096)
            except socket.timeout:
                pass

        # Progress report every 10%
        percent = (i + 1) * 100 // file_size
        if percent >= last_report + 10:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (file_size - i - 1) / rate if rate > 0 else 0
            print(f"  {percent}% ({i+1}/{file_size}) - {rate:.0f} bytes/sec - ETA: {eta/60:.1f} min")
            last_report = percent

    # Send any remaining batch
    if batch:
        cmd = ''.join(batch).encode()
        sock.send(cmd)

    time.sleep(1)
    recv_all(sock, 1)

    # Exit and save
    print("\nSaving file...")
    sock.send(b"EX" + ESC_ESC)
    time.sleep(2)
    wait_for(sock, "$", 10, echo=False)

    elapsed = time.time() - start_time
    print(f"\nTransfer complete! {file_size} bytes in {elapsed:.1f} seconds ({file_size/elapsed:.0f} bytes/sec)")

    # Verify file was created
    print(f"\nVerifying {remote_name}...")
    sock.send(f"DIR {remote_name}\r".encode())
    time.sleep(2)
    resp = recv_all(sock, 2)
    print(resp)

    # Logout
    print("Logging out...")
    sock.send(b"BYE\r")
    time.sleep(1)
    sock.close()

    return True

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nAvailable data files:")
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'build', 'data')
        if os.path.exists(data_dir):
            for f in os.listdir(data_dir):
                path = os.path.join(data_dir, f)
                size = os.path.getsize(path)
                print(f"  {f}: {size} bytes ({size/1024:.1f} KB)")
        sys.exit(1)

    local_path = sys.argv[1]
    remote_name = sys.argv[2]

    if not os.path.exists(local_path):
        print(f"Error: {local_path} not found")
        sys.exit(1)

    # RSTS/E filename restrictions
    if len(remote_name) > 9 or '.' not in remote_name:
        print(f"Warning: RSTS/E filenames should be NAME.EXT format (max 6.3)")

    transfer_file(local_path, remote_name)

if __name__ == '__main__':
    main()
