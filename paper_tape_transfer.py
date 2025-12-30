#!/usr/bin/env python3
"""Transfer file via SIMH paper tape emulation."""

import socket
import time
import sys

def send_to_simh_console(commands, port=2322):
    """Send commands to SIMH console."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(10)
    try:
        sock.connect(('localhost', port))
        time.sleep(0.5)

        # Read any initial data
        try:
            data = sock.recv(4096)
            print(f"Initial: {data[:200]}")
        except socket.timeout:
            pass

        for cmd in commands:
            print(f"Sending: {repr(cmd)}")
            sock.send(cmd.encode() if isinstance(cmd, str) else cmd)
            time.sleep(0.5)
            try:
                data = sock.recv(4096)
                print(f"Response: {data.decode('latin-1', errors='replace')[:500]}")
            except socket.timeout:
                print("(no response)")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        sock.close()

def main():
    file_to_transfer = sys.argv[1] if len(sys.argv) > 1 else "/home/edward/advent/src/ADVINI.SUB"

    print("=" * 60)
    print(f"Paper Tape Transfer: {file_to_transfer}")
    print("=" * 60)

    # Step 1: Break into SIMH monitor with Ctrl+E
    print("\n=== Step 1: Breaking into SIMH monitor ===")

    # Ctrl+E = ASCII 0x05
    ctrl_e = b'\x05'

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect(('localhost', 2322))
        print("Connected to SIMH console (port 2322)")

        # Send Ctrl+E to break
        sock.send(ctrl_e)
        time.sleep(1)

        # Try to read response
        try:
            data = sock.recv(4096)
            response = data.decode('latin-1', errors='replace')
            print(f"Response: {response[:500]}")

            if 'sim>' in response.lower():
                print("Got SIMH prompt!")

                # Attach paper tape
                cmd = f"attach ptr {file_to_transfer}\r\n"
                print(f"Sending: {cmd.strip()}")
                sock.send(cmd.encode())
                time.sleep(1)

                data = sock.recv(4096)
                print(f"Attach response: {data.decode('latin-1', errors='replace')}")

                # Show ptr status
                sock.send(b"show ptr\r\n")
                time.sleep(0.5)
                data = sock.recv(4096)
                print(f"PTR status: {data.decode('latin-1', errors='replace')}")

                # Continue execution
                sock.send(b"cont\r\n")
                time.sleep(0.5)
                print("Sent continue command")

        except socket.timeout:
            print("No response (timeout)")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

    print("\n=== Step 2: Now use RSTS/E to copy from PR: ===")
    print("Connect to port 2323 and run: COPY PR: DM1:[1,2]ADVINI.SUB")

if __name__ == '__main__':
    main()
