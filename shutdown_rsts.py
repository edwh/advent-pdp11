#!/usr/bin/env python3
"""Properly shut down RSTS to allow disk modification."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Properly Shut Down RSTS/E")
    print("=" * 60)

    child = pexpect.spawn('telnet localhost 2323', encoding='latin-1')
    child.logfile = sys.stdout

    try:
        child.expect('Connected to the PDP-11', timeout=10)
    except pexpect.TIMEOUT:
        print("\n*** Cannot connect ***")
        return False

    time.sleep(2)
    child.sendline('')
    time.sleep(1)
    child.sendline('')
    time.sleep(1)

    # Login as SYSTEM
    idx = child.expect(['User:', r'\$ ', 'Job number'], timeout=30)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        idx2 = child.expect(['Job number', r'\$ '], timeout=15)
        if idx2 == 0:
            child.sendline('')
    elif idx == 2:
        child.sendline('')

    child.expect(r'\$ ', timeout=30)
    print("\n*** Logged in ***")

    # Run SHUTUP to properly shutdown
    print("\n=== Running SHUTUP ===")
    child.sendline('RUN $SHUTUP')

    # Wait for prompts and respond
    while True:
        idx = child.expect([
            'Yes or No',
            'Rundown options',
            'How long until rundown',
            'Rundown type',
            'Final rundown',
            'Please press',
            'Rundown complete',
            'ready to halt',
            pexpect.TIMEOUT,
            r'\$ '
        ], timeout=60)

        if idx == 0:  # Yes or No
            child.sendline('YES')
        elif idx == 1:  # Rundown options
            child.sendline('')  # Accept default
        elif idx == 2:  # How long
            child.sendline('0')  # Immediate
        elif idx == 3:  # Rundown type
            child.sendline('3')  # Quick shutdown
        elif idx == 4:  # Final rundown
            child.sendline('YES')
        elif idx == 5:  # Please press
            child.sendline('')
        elif idx == 6:  # Rundown complete
            print("\n*** Rundown complete ***")
            break
        elif idx == 7:  # Ready to halt
            print("\n*** Ready to halt ***")
            break
        elif idx == 8:  # Timeout
            print("\n*** Timeout ***")
            break
        elif idx == 9:  # DCL prompt - abort?
            print("\n*** Back at DCL - shutup may have failed ***")
            break

    time.sleep(2)
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
