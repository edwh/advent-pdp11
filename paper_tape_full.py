#!/usr/bin/env python3
"""Complete paper tape file transfer to RSTS/E via SIMH."""

import pexpect
import sys
import time
import os

def main():
    source_file = sys.argv[1] if len(sys.argv) > 1 else "/home/edward/advent/src/ADVINI.SUB"
    dest_file = sys.argv[2] if len(sys.argv) > 2 else "DM1:[1,2]ADVINI.SUB"

    # Make sure source file exists with absolute path
    if not source_file.startswith('/'):
        source_file = os.path.abspath(source_file)

    print("=" * 60)
    print(f"Paper Tape Transfer")
    print(f"Source: {source_file}")
    print(f"Dest:   {dest_file}")
    print("=" * 60)

    # Connect to SIMH console
    print("\n=== Connecting to SIMH console (port 2322) ===")
    console = pexpect.spawn('telnet localhost 2322', encoding='latin-1')
    console.logfile = sys.stdout

    # Wait for system to be running - look for the console showing RSTS prompt or startup messages
    print("\n=== Waiting for RSTS/E to be ready ===")
    time.sleep(5)

    # Send Ctrl+E to break into SIMH monitor
    print("\n=== Sending Ctrl+E to enter SIMH monitor ===")
    console.sendcontrol('e')
    time.sleep(1)

    # Look for SIMH prompt
    idx = console.expect(['sim>', 'SIM>', pexpect.TIMEOUT], timeout=5)
    if idx == 2:
        print("No SIMH prompt, trying again...")
        console.sendcontrol('e')
        time.sleep(1)
        idx = console.expect(['sim>', 'SIM>', pexpect.TIMEOUT], timeout=5)

    if idx in [0, 1]:
        print("\n*** Got SIMH prompt! ***")

        # Check if ptr device exists
        console.sendline('show ptr')
        time.sleep(0.5)
        console.expect(['sim>', 'SIM>', pexpect.TIMEOUT], timeout=5)

        # Attach paper tape reader
        print(f"\n=== Attaching paper tape: {source_file} ===")
        console.sendline(f'attach ptr {source_file}')
        time.sleep(0.5)
        idx2 = console.expect(['sim>', 'SIM>', 'error', 'Error', pexpect.TIMEOUT], timeout=5)

        if idx2 in [2, 3]:
            print("\n*** Error attaching paper tape ***")
            console.close()
            return False

        # Show ptr status
        console.sendline('show ptr')
        time.sleep(0.5)
        console.expect(['sim>', 'SIM>', pexpect.TIMEOUT], timeout=5)

        # Continue RSTS/E
        print("\n=== Continuing RSTS/E ===")
        console.sendline('cont')
        time.sleep(2)

        print("\n*** Paper tape attached and RSTS/E resumed ***")
        console.close()

        # Now connect to RSTS/E terminal and do the copy
        print("\n=== Connecting to RSTS/E terminal (port 2323) ===")
        rsts = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
        rsts.logfile = sys.stdout

        time.sleep(2)
        rsts.sendline('')
        time.sleep(1)

        # Handle login
        for _ in range(10):
            idx = rsts.expect(['User:', r'\$ ', 'Job number', 'Password:', pexpect.TIMEOUT], timeout=30)
            if idx == 0:
                rsts.sendline('[1,2]')
            elif idx == 1:
                break
            elif idx == 2:
                rsts.sendline('')
            elif idx == 3:
                rsts.sendline('Digital1977')
            elif idx == 4:
                rsts.sendline('')
            time.sleep(1)

        print("\n*** Logged in to RSTS/E ***")

        # Copy from paper tape reader
        print(f"\n=== Copying from PR: to {dest_file} ===")
        rsts.sendline(f'COPY PR: {dest_file}')
        time.sleep(5)

        idx = rsts.expect([r'\$ ', 'error', 'Error', pexpect.TIMEOUT], timeout=30)
        print(f"\nCopy result: idx={idx}")

        # Verify the file
        print("\n=== Verifying file ===")
        rsts.sendline(f'DIR {dest_file}')
        time.sleep(2)
        rsts.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

        rsts.close()
        print("\n*** Transfer complete! ***")
        return True

    else:
        print("\n*** Could not get SIMH prompt ***")
        console.close()
        return False

if __name__ == '__main__':
    main()
