#!/usr/bin/env python3
"""Properly shutdown RSTS/E - answer all prompts."""

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

    # Try SHUTUP command
    print("\n=== Running SHUTUP ===")
    child.sendline('RUN $SHUTUP')
    time.sleep(3)

    # Answer prompts until we're done
    for _ in range(30):
        idx = child.expect([
            r'\?',           # Any question prompt
            'Option',        # Option prompt
            'halted',        # System halted
            'HALT',          # HALT message
            r'\$ ',          # DCL prompt
            pexpect.TIMEOUT
        ], timeout=30)

        print(f"\nPrompt idx={idx}")

        if idx == 0:
            # Question - answer with default (just press enter) or NO for jobs
            child.sendline('')
            time.sleep(1)
        elif idx == 1:
            # Option menu - select RUNDOWN
            child.sendline('RUNDOWN')
            time.sleep(1)
        elif idx in [2, 3]:
            # System halted
            print("\n*** System halted! ***")
            break
        elif idx == 4:
            # Back to DCL prompt
            print("\n*** Back at DCL - SHUTUP may have exited ***")
            break
        elif idx == 5:
            # Timeout
            child.sendline('')
            time.sleep(1)

    child.close()
    print("\n*** Done ***")
    return True

if __name__ == '__main__':
    main()
