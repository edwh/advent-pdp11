#!/usr/bin/env python3
"""Find BP2OTS library and build ADVENT."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Find Library and Build ADVENT")
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

    # Find the BP2OTS library
    print("\n=== Finding BP2OTS library ===")
    dcl_cmd('DIR SY:BP2OTS.*')
    dcl_cmd('DIR SY:[1,1]BP2OTS.*')
    dcl_cmd('DIR LB:BP2OTS.*')

    # Check what LB: is assigned to
    print("\n=== Checking LB: assignment ===")
    dcl_cmd('SHOW ASSIGN LB:')

    # Run TKB with correct library path
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Use explicit path to library
    child.sendline('DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,SY:[1,1]BP2OTS/LB')

    idx = child.expect(['TKB>', 'Enter Options:', 'FATAL', 'error', r'\$ ', pexpect.TIMEOUT], timeout=60)

    if idx == 0:
        child.sendline('/')
        idx2 = child.expect(['TKB>', 'Enter Options:', r'\$ '], timeout=60)
        if idx2 == 1:
            child.sendline('')
            child.expect(['TKB>', r'\$ '], timeout=60)
        if idx2 != 2:
            child.expect(r'\$ ', timeout=60)
    elif idx == 1:
        child.sendline('')
        child.expect(['TKB>', r'\$ '], timeout=60)
        child.expect(r'\$ ', timeout=60)
    elif idx in [2, 3]:
        print(f"\n*** TKB Error ***")
        child.expect(['TKB>', r'\$ '], timeout=30)
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)

    # Check result
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
