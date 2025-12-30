#!/usr/bin/env python3
"""Check the original ODL file for proper overlay structure."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Check Original ODL File")
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

    def dcl_cmd(cmd, timeout=15):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # Create logical name
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Check original ODL file
    print("\n=== Original ADVENT.ODL ===")
    child.sendline('TYPE A:ADVENT.ODL')
    time.sleep(5)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Check if there's a LIBR.ODL
    print("\n=== Checking for LIBR.ODL ===")
    child.sendline('TYPE A:LIBR.ODL')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # List all OBJ files with sizes
    print("\n=== OBJ files ===")
    child.sendline('DIR/SIZE A:*.OBJ')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Check if we already have ADVENT.TSK from original
    print("\n=== Looking for original TSK ===")
    child.sendline('DIR/SIZE A:*.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
