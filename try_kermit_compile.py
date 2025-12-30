#!/usr/bin/env python3
"""Try to compile KERMIT.MAC on RSTS/E."""

import pexpect
import sys
import time

def main():
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
    for _ in range(10):
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

    # Check what KERMIT.MAC contains
    print("\n=== View KERMIT.MAC ===")
    child.sendline('TYPE DM1:[1,3]KERMIT.MAC')
    time.sleep(5)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Check for MACRO-11 assembler
    print("\n=== Looking for MACRO assembler ===")
    child.sendline('DIR SY:[1,2]*.TSK')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Try to find RUN $MACRO or similar
    print("\n=== Try RUN $MACRO ===")
    child.sendline('RUN $MACRO')
    time.sleep(2)
    idx = child.expect([r'\$ ', r'\*', 'not found', 'No such', pexpect.TIMEOUT], timeout=10)
    print(f"\nMACRO result: idx={idx}")

    if idx == 1:
        # Got MACRO prompt
        print("\n=== MACRO assembler found! Exiting... ===")
        child.sendline(chr(26))  # Ctrl+Z
        time.sleep(1)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Check for other file transfer utilities
    print("\n=== Looking for transfer utilities ===")
    child.sendline('DIR SY:[*,*]KERMIT.*')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    child.sendline('DIR SY:[*,*]K11*.*')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Check for FIT (File Interchange Transfer)
    print("\n=== Looking for FIT ===")
    child.sendline('DIR SY:FIT.*')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Check HELP for file transfer
    print("\n=== HELP COPY ===")
    child.sendline('HELP COPY')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    child.close()
    print("\n*** Done ***")
    return True

if __name__ == '__main__':
    main()
