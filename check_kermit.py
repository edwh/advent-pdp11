#!/usr/bin/env python3
"""Check for Kermit on RL02 disk."""

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

    def dcl_cmd(cmd, timeout=30):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # Check for RL02 disk (DL0:)
    print("\n=== SHOW DEVICES (looking for RL02/DL:) ===")
    dcl_cmd('SHOW DEVICES')

    # Try to access DL0:
    print("\n=== Trying to access DL0: ===")
    child.sendline('DIR DL0:')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Try mounting it
    print("\n=== Trying MOUNT DL0: ===")
    child.sendline('MOUNT DL0: KERMIT')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Check devices again
    print("\n=== SHOW DEVICES after mount ===")
    dcl_cmd('SHOW DEVICES')

    # List the Kermit disk if mounted
    print("\n=== DIR DL0: ===")
    child.sendline('DIR DL0:')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Try [11,6] account
    print("\n=== DIR DL0:[11,6] ===")
    child.sendline('DIR DL0:[11,6]')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Look for Kermit executable
    print("\n=== DIR DL0:[*,*]*.TSK ===")
    child.sendline('DIR DL0:[*,*]*.TSK')
    time.sleep(5)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    child.close()
    print("\n*** Done ***")
    return True

if __name__ == '__main__':
    main()
