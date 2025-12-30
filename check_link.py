#!/usr/bin/env python3
"""Check LINK command capabilities."""

import pexpect
import sys
import time

def main():
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

    # Login
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

    # Install BP2RES
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check HELP LINK
    print("\n=== HELP LINK ===")
    child.sendline('HELP LINK')
    time.sleep(3)
    child.sendline('')  # Press enter for more
    time.sleep(2)
    child.sendline('')
    time.sleep(2)
    idx = child.expect([r'\$ ', 'Topic', pexpect.TIMEOUT], timeout=30)
    if idx == 1:
        child.sendline('')  # Exit help
        child.expect(r'\$ ', timeout=10)

    # Try LINK command directly
    print("\n=== Testing LINK command ===")
    child.sendline('LINK')
    time.sleep(2)
    idx = child.expect([r'\$ ', '>', 'File:', pexpect.TIMEOUT], timeout=15)
    print(f"\n*** LINK result: idx={idx} ***")

    if idx == 2:
        # LINK wants a file - give it ADVENT
        child.sendline('DM1:[1,2]ADVENT')
        time.sleep(3)
        child.expect([r'\$ ', '>', pexpect.TIMEOUT], timeout=30)

    # Check what $ programs exist
    print("\n=== Checking $TKB ===")
    child.sendline('DIR $TKB')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    child.close()
    return True

if __name__ == '__main__':
    main()
