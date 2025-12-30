#!/usr/bin/env python3
"""Check if .SUB files exist on RSTS/E disk."""

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

    # Check for SUB files
    print("\n=== Checking for .SUB files on DM1:[1,2] ===")
    dcl_cmd('DIR DM1:[1,2]*.SUB')

    # Check for B2S files
    print("\n=== Checking for .B2S files on DM1:[1,2] ===")
    dcl_cmd('DIR DM1:[1,2]*.B2S')

    # Also check SY:[1,2]
    print("\n=== Checking for .SUB files on SY:[1,2] ===")
    dcl_cmd('DIR SY:[1,2]*.SUB')

    print("\n=== Checking for .B2S files on SY:[1,2] ===")
    dcl_cmd('DIR SY:[1,2]*.B2S')

    child.close()
    return True

if __name__ == '__main__':
    main()
