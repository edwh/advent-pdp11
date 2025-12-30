#!/usr/bin/env python3
"""Check TKB.CTL file."""

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

    def dcl_cmd(cmd, timeout=15):
        child.sendline(cmd)
        child.expect(r'\$ ', timeout=timeout)
        time.sleep(0.5)

    # Check TKB.CTL
    print("\n=== TKB.CTL ===")
    dcl_cmd('TYPE DM1:[1,2]TKB.CTL')

    # Check if there's a LINK or BUILD command in RSTS
    print("\n=== Help LINK ===")
    dcl_cmd('HELP LINK', timeout=30)

    # Try using @ in DCL context
    print("\n=== Testing @ in DCL ===")
    child.sendline('@DM1:[1,2]TKB.CMD')
    time.sleep(5)
    idx = child.expect([r'\$ ', 'TKB>', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** idx={idx} ***")

    child.close()
    return True

if __name__ == '__main__':
    main()
