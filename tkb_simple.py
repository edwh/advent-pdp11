#!/usr/bin/env python3
"""Build ADVENT.TSK using TKB with simpler syntax."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK using TKB (Simple)")
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

    # Run TKB with simpler syntax
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Try just the main program first (without overlays)
    # Simple format: output=main,library
    child.sendline('DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,LB:BP2OTS/LB')

    idx = child.expect(['TKB>', 'FATAL', 'error', 'Enter Options:', r'\$ ', pexpect.TIMEOUT], timeout=60)

    if idx in [0, 3]:
        # At prompt - send / to finish
        if idx == 3:
            child.sendline('')  # Accept default options
            child.expect('TKB>', timeout=30)
        child.sendline('/')
        child.expect([r'\$ ', 'TKB>'], timeout=60)
        if child.match:
            if b'TKB' in child.after:
                child.sendline('')
                child.expect(r'\$ ', timeout=30)
    elif idx in [1, 2]:
        print(f"\n*** TKB Error ***")
        child.expect(['TKB>', r'\$ '], timeout=30)
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)

    # Check for TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # Try running it if it exists
    child.sendline('RUN DM1:[1,2]ADVENT')
    idx = child.expect(['Welcome', 'name', '>', 'Error', r'\?', r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** Game result: {idx} ***")

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
