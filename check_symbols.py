#!/usr/bin/env python3
"""Check undefined symbols in map file."""

import pexpect
import sys
import time

def main():
    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)

    # Handle login
    while True:
        idx = child.expect(['User:', r'\$ ', 'Job number', 'Password:'], timeout=30)
        if idx == 0:
            child.sendline('[1,2]')
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')
        elif idx == 3:
            child.sendline('Digital1977')
        time.sleep(1)

    print("\n*** Logged in ***")

    # View the map file to find undefined symbols
    print("\n=== Searching for undefined symbols ===")
    child.sendline('TYPE DM1:[1,2]ADVENT.MAP')
    time.sleep(2)

    # Scroll through the file looking for "undefined"
    for _ in range(20):
        idx = child.expect(['Press RETURN', r'\$ ', 'Undefined', 'undefined', pexpect.TIMEOUT], timeout=10)
        if idx in [0]:
            child.sendline('')
            time.sleep(1)
        elif idx == 1:
            break
        elif idx in [2, 3]:
            print("\n*** Found undefined symbols! ***")
            time.sleep(1)
        else:
            child.sendline('')
            time.sleep(1)

    # Use GREP-like search if available
    print("\n=== Looking for linker errors at end of map ===")
    # The TKB errors usually appear after the symbol table
    child.sendline('DIR/SIZE DM1:[1,2]ADVENT.MAP')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Check the linking result messages
    # They should be at the beginning after initial header
    print("\n=== First 100 lines of map file ===")
    child.sendline('TYPE/PAGE DM1:[1,2]ADVENT.MAP')
    time.sleep(3)

    # Read a few pages
    for _ in range(5):
        idx = child.expect(['Press RETURN', r'\$ ', pexpect.TIMEOUT], timeout=10)
        if idx == 0:
            child.sendline('')
            time.sleep(1)
        else:
            break

    child.close()
    print("\n*** DONE ***")
    return True

if __name__ == '__main__':
    main()
