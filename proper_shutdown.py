#!/usr/bin/env python3
"""Properly shutdown RSTS/E to fix disk dismount state."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Proper RSTS/E shutdown")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("ERROR: Could not connect")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # Login
    while True:
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:', pexpect.TIMEOUT], timeout=30)
        if idx == 0:
            child.sendline('[1,2]')
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')
        elif idx == 3:
            child.sendline('Digital1977')
        elif idx == 4:
            child.sendline('')
        time.sleep(1)

    print("\n*** Logged in ***")

    # Try SHUTUP command for proper shutdown
    print("\n=== Trying SHUTUP ===")
    child.sendline('RUN $SHUTUP')
    time.sleep(3)

    idx = child.expect(['Option', 'SHUTUP', 'option', r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\nSHUTUP result: idx={idx}")

    if idx in [0, 1, 2]:
        # In SHUTUP - request shutdown
        child.sendline('RUNDOWN')
        time.sleep(3)
        idx2 = child.expect(['Rundown', 'rundown', 'minutes', 'Option', pexpect.TIMEOUT], timeout=30)
        print(f"\nRundown result: idx={idx2}")

        # Provide time - immediate
        child.sendline('0')
        time.sleep(5)

        # Wait for shutdown messages
        for _ in range(10):
            idx3 = child.expect(['shut', 'dismount', 'Option', 'halted', pexpect.TIMEOUT], timeout=30)
            print(f"\nShutdown progress: idx={idx3}")
            if idx3 == 3 or idx3 == 4:
                break
            time.sleep(2)

    child.close()
    print("\n*** Shutdown attempted ***")
    return True

if __name__ == '__main__':
    main()
