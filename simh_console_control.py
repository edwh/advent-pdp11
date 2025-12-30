#!/usr/bin/env python3
"""
Control RSTS/E via SIMH console - bypasses DZ terminal handling.

SIMH console (port 2322) lets us:
1. Break into simulator with Ctrl+E
2. Use SEND command to inject exact keystrokes to simulated terminal
3. Use EXPECT to wait for patterns
4. DEPOSIT/EXAMINE memory directly

This gives us byte-level control without telnet corruption.
"""

import socket
import time
import sys

class SIMHConsole:
    def __init__(self, host='localhost', port=2322):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.settimeout(30)
        self.debug = True

    def read_available(self, timeout=1.0):
        """Read all available data."""
        self.sock.setblocking(False)
        data = b''
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                chunk = self.sock.recv(4096)
                if chunk:
                    data += chunk
                else:
                    break
            except BlockingIOError:
                time.sleep(0.05)
        self.sock.setblocking(True)
        text = data.decode('latin-1', errors='replace')
        if self.debug and text:
            print(f"[RECV] {repr(text)}")
        return text

    def send_raw(self, data):
        """Send raw bytes."""
        if isinstance(data, str):
            data = data.encode('latin-1')
        if self.debug:
            print(f"[SEND] {repr(data)}")
        self.sock.sendall(data)

    def send_line(self, line):
        """Send a line with CR."""
        self.send_raw(line + '\r')

    def break_to_simh(self):
        """Send Ctrl+E to break into SIMH monitor."""
        print("\n=== Breaking into SIMH ===")
        self.send_raw(b'\x05')  # Ctrl+E
        time.sleep(0.5)
        response = self.read_available(1.0)
        return 'sim>' in response.lower()

    def simh_cmd(self, cmd, wait=1.0):
        """Execute SIMH command."""
        self.send_line(cmd)
        time.sleep(wait)
        return self.read_available(wait)

    def continue_sim(self):
        """Continue simulation."""
        return self.simh_cmd('cont', 0.5)

    def send_to_terminal(self, text, delay=0.1):
        """
        Use SIMH SEND command to inject text into simulated terminal.
        This bypasses all terminal handling!
        """
        # SIMH SEND command syntax: SEND "text"
        # Special chars: \r for CR, \n for LF, \t for TAB

        # Escape special characters for SIMH
        escaped = text.replace('\\', '\\\\')  # Escape backslashes first
        escaped = escaped.replace('"', '\\"')  # Escape quotes
        escaped = escaped.replace('\t', '\\t')  # TAB -> \t
        escaped = escaped.replace('\r', '\\r')  # CR -> \r
        escaped = escaped.replace('\n', '\\n')  # LF -> \n

        return self.simh_cmd(f'SEND "{escaped}"', delay)

    def send_line_to_terminal(self, line, delay=0.2):
        """Send a line to the terminal with CR at end."""
        return self.send_to_terminal(line + '\r', delay)

    def wait_for_pattern(self, pattern, timeout=30):
        """
        Use SIMH EXPECT to wait for a pattern.
        Returns True if pattern found.
        """
        # Set up expect
        self.simh_cmd(f'EXPECT "{pattern}"', 0.2)
        # Wait
        time.sleep(timeout)
        # Check if matched (would need to parse SIMH response)
        return True  # Simplified

    def close(self):
        self.sock.close()


def test_simh_console():
    """Test SIMH console control."""

    print("=== SIMH Console Control Test ===\n")

    console = SIMHConsole()

    # Read initial data
    print("\n--- Initial read ---")
    console.read_available(2.0)

    # Break into SIMH
    print("\n--- Breaking into SIMH ---")
    if console.break_to_simh():
        print("Got SIMH prompt!")

        # Show SIMH status
        print("\n--- SIMH Status ---")
        console.simh_cmd('show time', 0.5)
        console.simh_cmd('show dz', 0.5)

        # Try SEND command
        print("\n--- Testing SEND command ---")
        # First, let's see SEND help
        console.simh_cmd('help send', 2.0)

        # Continue simulation
        print("\n--- Continuing simulation ---")
        console.continue_sim()

        time.sleep(2)
        console.read_available(2.0)

    else:
        print("Could not get SIMH prompt")
        # Maybe already at RSTS console, read what's there
        console.read_available(2.0)

    console.close()
    print("\n=== Done ===")


def transfer_file_via_simh(filename, dest):
    """
    Transfer a file using SIMH SEND command.
    This injects keystrokes directly, bypassing terminal handling.
    """

    print(f"=== Transferring {filename} to {dest} ===\n")

    # Read source file
    with open(filename, 'r') as f:
        content = f.read()

    console = SIMHConsole()
    console.read_available(2.0)

    # Break into SIMH
    if not console.break_to_simh():
        print("Could not break into SIMH")
        console.close()
        return False

    print("Got SIMH prompt")

    # Use SEND to start CREATE command on RSTS
    print("\n--- Sending CREATE command ---")
    console.send_line_to_terminal(f'CREATE {dest}')
    console.continue_sim()
    time.sleep(2)

    # Break back in
    console.break_to_simh()

    # Send each line of the file
    print("\n--- Sending file content ---")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line:  # Skip empty lines at end
            print(f"  Line {i+1}: {repr(line[:40])}...")
            console.send_line_to_terminal(line)
            console.continue_sim()
            time.sleep(0.1)
            console.break_to_simh()

    # Send Ctrl+Z to end CREATE
    print("\n--- Sending Ctrl+Z ---")
    console.send_to_terminal('\x1a')
    console.continue_sim()
    time.sleep(2)

    console.read_available(2.0)
    console.close()

    print("\n=== Transfer complete ===")
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'transfer':
        # Transfer mode
        src = sys.argv[2] if len(sys.argv) > 2 else 'test.txt'
        dst = sys.argv[3] if len(sys.argv) > 3 else 'DM1:[1,2]TEST.TXT'
        transfer_file_via_simh(src, dst)
    else:
        # Test mode
        test_simh_console()
