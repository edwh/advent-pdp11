#!/usr/bin/env python3
"""Build ADVENT.TSK - Final version with proper TKB handling."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Final")
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
        time.sleep(0.3)

    # Run TKB
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Build command - use LB: which is assigned to SY:[1,1]
    child.sendline('DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,LB:BP2OTS/LB')
    child.expect('TKB>', timeout=60)

    # Send / to end file specification
    child.sendline('/')

    # Wait for "Enter Options:" prompt
    child.expect('Enter Options:', timeout=30)

    # Accept default options with empty line
    child.sendline('')

    # Wait for build to complete - may take a while
    idx = child.expect([r'\$ ', 'TKB>', 'error', 'FATAL', pexpect.TIMEOUT], timeout=180)

    if idx == 0:
        print("\n*** Build completed ***")
    elif idx == 1:
        # Still at TKB prompt - might need another /
        child.sendline('/')
        child.expect(r'\$ ', timeout=60)
    elif idx in [2, 3]:
        print("\n*** Build error ***")
        child.expect([r'\$ ', 'TKB>'], timeout=30)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # If exists, test it
    child.sendline('RUN DM1:[1,2]ADVENT')
    idx = child.expect(['Welcome', 'name', '>', 'file', r'\?', r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** Game test: {idx} ***")

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
