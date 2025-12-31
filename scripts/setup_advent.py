#!/usr/bin/env python3
"""
ADVENT MUD Complete Setup Script

This script automates the complete setup of ADVENT MUD on RSTS/E:
1. Waits for RSTS/E to boot
2. Logs in
3. Transfers all data files (binary via TECO)
4. Transfers all source files (ASCII via TECO)
5. Compiles all source files with BP2
6. Links the executable with TKB
7. Verifies the installation

Usage:
    python3 setup_advent.py [--skip-data] [--skip-source] [--skip-compile]
"""

import socket
import time
import sys
import os
import argparse

# Connection settings
HOST = os.environ.get('RSTS_HOST', 'localhost')
PORT = int(os.environ.get('RSTS_PORT', '2323'))
USER = os.environ.get('RSTS_USER', '[1,2]')
PASSWORD = os.environ.get('RSTS_PASSWORD', 'Digital1977')

# TECO escape sequence
ESC = b'\x1b'
ESC_ESC = b'\x1b\x1b'

# Data files to transfer (binary)
DATA_FILES = [
    ('ADVENT.DTA', 1024000),  # Room data
    ('ADVENT.MON', 200000),   # Monster data
    ('ADVENT.CHR', 51200),    # Character data
    ('BOARD.NTC', 262144),    # Bulletin board
    ('MESSAG.NPC', 60000),    # NPC messages
]

# Source files to transfer (ASCII)
SOURCE_FILES = [
    'ADVENT.B2S',   # Main program
    'ADVINI.SUB',   # Initialization
    'ADVDSP.SUB',   # Display/LOOK
    'ADVNOR.SUB',   # Navigation/movement
    'ADVCMD.SUB',   # Commands
    'ADVMSG.SUB',   # Messages
    'ADVBYE.SUB',   # Exit handling
    'ADVFND.SUB',   # Find functions
    'ADVNPC.SUB',   # NPC handling
    'ADVODD.SUB',   # Miscellaneous
    'ADVOUT.SUB',   # Output
    'ADVPUZ.SUB',   # Puzzles
    'ADVSHT.SUB',   # Short commands
    'ADVTDY.SUB',   # Tidy/cleanup
]

class RSTSConnection:
    """Handle connection to RSTS/E via telnet."""

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Connect to RSTS/E."""
        print(f"Connecting to {self.host}:{self.port}...")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        time.sleep(2)
        self.recv_all(2)

    def close(self):
        """Close connection."""
        if self.sock:
            self.sock.close()
            self.sock = None

    def recv_all(self, timeout=2):
        """Receive all available data with timeout."""
        self.sock.settimeout(timeout)
        data = b""
        try:
            while True:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
        return data.decode('latin-1')

    def wait_for(self, pattern, timeout=30, echo=False):
        """Wait for a pattern to appear in the response."""
        self.sock.settimeout(1)
        data = ""
        start = time.time()
        while time.time() - start < timeout:
            try:
                chunk = self.sock.recv(4096).decode('latin-1')
                data += chunk
                if echo:
                    print(chunk, end='', flush=True)
                if pattern in data:
                    return data
            except socket.timeout:
                pass
        return data

    def send(self, data):
        """Send data."""
        if isinstance(data, str):
            data = data.encode()
        self.sock.send(data)

    def login(self):
        """Login to RSTS/E."""
        print("Logging in...")
        self.send(b"\r")
        time.sleep(1)
        self.wait_for("User:", 10)
        self.send(f"{USER}\r")
        self.wait_for("Password:", 10)
        self.send(f"{PASSWORD}\r")
        time.sleep(2)
        resp = self.wait_for("$", 10)

        # Handle detached job prompt
        if "Job number" in resp:
            self.send(b"\r")
            self.wait_for("$", 10)
        print("Logged in!")

    def logout(self):
        """Logout from RSTS/E."""
        print("Logging out...")
        self.send(b"BYE\r")
        time.sleep(1)
        self.recv_all(1)


def wait_for_rsts(host, port, max_wait=120):
    """Wait for RSTS/E to be ready for connections."""
    print(f"Waiting for RSTS/E at {host}:{port}...")
    start = time.time()

    while time.time() - start < max_wait:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((host, port))
            sock.close()
            print("RSTS/E is ready!")
            # Give it a bit more time to fully initialize
            time.sleep(5)
            return True
        except (socket.error, socket.timeout):
            print(".", end="", flush=True)
            time.sleep(2)

    print("\nTimeout waiting for RSTS/E!")
    return False


def transfer_binary_file(conn, local_path, remote_name):
    """Transfer a binary file using TECO's nI command."""
    print(f"\nTransferring {remote_name}...")

    # Read local file
    with open(local_path, 'rb') as f:
        data = f.read()
    file_size = len(data)
    print(f"  Size: {file_size} bytes")

    # Delete existing file
    conn.send(f"DELETE {remote_name}\r")
    time.sleep(1)
    conn.recv_all(1)

    # Start TECO
    conn.send(b"TECO\r")
    time.sleep(1)
    conn.wait_for("*", 5, echo=False)

    # Open output file
    conn.send(f"EW{remote_name}".encode() + ESC_ESC)
    time.sleep(0.5)
    conn.recv_all(0.5)

    # Transfer data
    BATCH_SIZE = 100
    CHUNK_SIZE = 500
    start_time = time.time()
    last_report = 0
    chunk_count = 0

    batch = []
    for i, byte_val in enumerate(data):
        batch.append(f"{byte_val}I\x1b\x1b")
        chunk_count += 1

        if len(batch) >= BATCH_SIZE:
            conn.send(''.join(batch).encode())
            batch = []
            time.sleep(0.02)
            try:
                conn.sock.settimeout(0.01)
                conn.sock.recv(4096)
            except socket.timeout:
                pass

        if chunk_count >= CHUNK_SIZE:
            conn.send(b"P\x1b\x1b")
            time.sleep(0.1)
            conn.recv_all(0.1)
            chunk_count = 0

        # Progress report every 10%
        percent = (i + 1) * 100 // file_size
        if percent >= last_report + 10:
            elapsed = time.time() - start_time
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            eta = (file_size - i - 1) / rate if rate > 0 else 0
            print(f"    {percent}% ({i+1}/{file_size}) - {rate:.0f} B/s - ETA: {eta/60:.1f} min")
            last_report = percent

    # Flush remaining batch
    if batch:
        conn.send(''.join(batch).encode())

    time.sleep(1)
    conn.recv_all(1)

    # Exit TECO and save
    conn.send(b"EX" + ESC_ESC)
    time.sleep(2)
    conn.wait_for("$", 10, echo=False)

    elapsed = time.time() - start_time
    print(f"  Done! {file_size} bytes in {elapsed:.0f}s ({file_size/elapsed:.0f} B/s)")

    # Verify
    conn.send(f"DIR {remote_name}\r")
    time.sleep(2)
    resp = conn.recv_all(2)
    if remote_name in resp:
        print(f"  Verified: {remote_name} exists on RSTS/E")
        return True
    else:
        print(f"  WARNING: Could not verify {remote_name}")
        return False


def transfer_ascii_file(conn, local_path, remote_name):
    """Transfer an ASCII file using TECO."""
    print(f"\nTransferring {remote_name}...")

    # Read local file
    with open(local_path, 'r', encoding='latin-1') as f:
        content = f.read()

    # Convert line endings to CR
    content = content.replace('\r\n', '\r').replace('\n', '\r')
    file_size = len(content)
    print(f"  Size: {file_size} bytes")

    # Delete existing file
    conn.send(f"DELETE {remote_name}\r")
    time.sleep(1)
    conn.recv_all(1)

    # Start TECO
    conn.send(b"TECO\r")
    time.sleep(1)
    conn.wait_for("*", 5, echo=False)

    # Open output file
    conn.send(f"EW{remote_name}".encode() + ESC_ESC)
    time.sleep(0.5)
    conn.recv_all(0.5)

    # For ASCII, we can use the I command with text directly
    # But we need to escape special characters
    # Use the same byte-by-byte approach for safety
    BATCH_SIZE = 100
    CHUNK_SIZE = 500
    start_time = time.time()
    chunk_count = 0

    batch = []
    for byte_val in content.encode('latin-1'):
        batch.append(f"{byte_val}I\x1b\x1b")
        chunk_count += 1

        if len(batch) >= BATCH_SIZE:
            conn.send(''.join(batch).encode())
            batch = []
            time.sleep(0.02)
            try:
                conn.sock.settimeout(0.01)
                conn.sock.recv(4096)
            except socket.timeout:
                pass

        if chunk_count >= CHUNK_SIZE:
            conn.send(b"P\x1b\x1b")
            time.sleep(0.1)
            conn.recv_all(0.1)
            chunk_count = 0

    # Flush remaining batch
    if batch:
        conn.send(''.join(batch).encode())

    time.sleep(1)
    conn.recv_all(1)

    # Exit TECO and save
    conn.send(b"EX" + ESC_ESC)
    time.sleep(2)
    conn.wait_for("$", 10, echo=False)

    elapsed = time.time() - start_time
    print(f"  Done! {file_size} bytes in {elapsed:.0f}s")

    return True


def compile_source(conn, source_name):
    """Compile a source file with BP2."""
    print(f"\nCompiling {source_name}...")

    # Determine output name
    base_name = source_name.rsplit('.', 1)[0]

    # Run BP2 compiler
    conn.send(b"RUN $BP2IC2\r")
    time.sleep(2)
    conn.wait_for("Ready", 10, echo=False)

    # Compile the file
    conn.send(f"COMPILE {source_name}\r")
    time.sleep(5)
    resp = conn.wait_for("Ready", 30, echo=False)

    if "error" in resp.lower():
        print(f"  ERROR compiling {source_name}:")
        print(resp)
        conn.send(b"\x03")  # Ctrl-C to exit
        time.sleep(1)
        conn.recv_all(1)
        return False

    print(f"  Compiled {source_name} -> {base_name}.OBJ")

    # Exit BP2
    conn.send(b"\x1a")  # Ctrl-Z
    time.sleep(1)
    conn.recv_all(1)

    return True


def link_advent(conn):
    """Link ADVENT.TSK using TKB."""
    print("\nLinking ADVENT.TSK...")

    # Start TKB
    conn.send(b"RUN $TKB\r")
    time.sleep(2)
    conn.wait_for("TKB>", 10, echo=False)

    # Provide linker commands
    # Output file, input files
    conn.send(b"ADVENT/FP=ADVENT,ADVINI,ADVDSP,ADVNOR,ADVCMD\r")
    time.sleep(1)
    conn.send(b"ADVMSG,ADVBYE,ADVFND,ADVNPC,ADVODD\r")
    time.sleep(1)
    conn.send(b"ADVOUT,ADVPUZ,ADVSHT,ADVTDY\r")
    time.sleep(1)
    conn.send(b"SY:BP2OTS/LB,SY:RMSRLX/LB\r")  # Libraries
    time.sleep(1)
    conn.send(b"//\r")  # End of input files
    time.sleep(1)
    conn.wait_for("TKB>", 10, echo=False)

    # No ODL file
    conn.send(b"\r")
    time.sleep(1)

    # Wait for linking to complete
    resp = conn.wait_for("$", 60, echo=False)

    if "error" in resp.lower():
        print("  ERROR linking:")
        print(resp)
        return False

    print("  Linked ADVENT.TSK successfully!")
    return True


def verify_installation(conn):
    """Verify the installation."""
    print("\nVerifying installation...")

    # Check ADVENT.TSK exists
    conn.send(b"DIR ADVENT.TSK\r")
    time.sleep(2)
    resp = conn.recv_all(2)

    if "ADVENT.TSK" in resp:
        print("  ADVENT.TSK exists")
    else:
        print("  WARNING: ADVENT.TSK not found!")
        return False

    # Check data files
    conn.send(b"DIR ADVENT.*\r")
    time.sleep(2)
    resp = conn.recv_all(2)
    print(f"  Data files:\n{resp}")

    return True


def main():
    parser = argparse.ArgumentParser(description='Setup ADVENT MUD on RSTS/E')
    parser.add_argument('--skip-data', action='store_true', help='Skip data file transfer')
    parser.add_argument('--skip-source', action='store_true', help='Skip source file transfer')
    parser.add_argument('--skip-compile', action='store_true', help='Skip compilation and linking')
    parser.add_argument('--data-dir', default=None, help='Path to data files')
    parser.add_argument('--source-dir', default=None, help='Path to source files')
    args = parser.parse_args()

    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)

    data_dir = args.data_dir or os.path.join(base_dir, 'build', 'data')
    source_dir = args.source_dir or os.path.join(base_dir, 'src')

    print("=" * 60)
    print("  ADVENT MUD Setup")
    print("=" * 60)
    print(f"Data directory: {data_dir}")
    print(f"Source directory: {source_dir}")
    print()

    # Wait for RSTS/E to be ready
    if not wait_for_rsts(HOST, PORT):
        sys.exit(1)

    # Connect and login
    conn = RSTSConnection(HOST, PORT)
    conn.connect()
    conn.login()

    try:
        # Transfer data files
        if not args.skip_data:
            print("\n" + "=" * 60)
            print("  Transferring Data Files")
            print("=" * 60)

            for filename, expected_size in DATA_FILES:
                local_path = os.path.join(data_dir, filename)
                if os.path.exists(local_path):
                    actual_size = os.path.getsize(local_path)
                    if actual_size != expected_size:
                        print(f"WARNING: {filename} size mismatch: {actual_size} vs {expected_size}")
                    transfer_binary_file(conn, local_path, filename)
                else:
                    print(f"WARNING: {local_path} not found, skipping")

        # Transfer source files
        if not args.skip_source:
            print("\n" + "=" * 60)
            print("  Transferring Source Files")
            print("=" * 60)

            for filename in SOURCE_FILES:
                local_path = os.path.join(source_dir, filename)
                if os.path.exists(local_path):
                    transfer_ascii_file(conn, local_path, filename)
                else:
                    print(f"WARNING: {local_path} not found, skipping")

        # Compile and link
        if not args.skip_compile:
            print("\n" + "=" * 60)
            print("  Compiling Source Files")
            print("=" * 60)

            for filename in SOURCE_FILES:
                compile_source(conn, filename)

            print("\n" + "=" * 60)
            print("  Linking Executable")
            print("=" * 60)
            link_advent(conn)

        # Verify
        verify_installation(conn)

        print("\n" + "=" * 60)
        print("  Setup Complete!")
        print("=" * 60)
        print("\nTo run the game:")
        print("  RUN ADVENT")

    finally:
        conn.logout()
        conn.close()


if __name__ == '__main__':
    main()
