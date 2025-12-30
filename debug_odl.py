#!/usr/bin/env python3
"""Debug ODL format by comparing with working system ODL files."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Debug ODL Format")
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

    # Find working ODL files on the system
    print("\n=== Looking for working ODL files ===")
    dcl_cmd('DIR SY:[1,1]*.ODL')
    dcl_cmd('DIR SY:[0,63]*.ODL')
    dcl_cmd('DIR SY:[0,65]*.ODL')

    # Look at a working ODL file
    print("\n=== Sample working ODL (BP2IC2.ODL) ===")
    dcl_cmd('TYPE SY:[1,1]BP2IC2.ODL')

    # Compare with our ODL
    print("\n=== Our ADVENT.ODL ===")
    dcl_cmd('TYPE DM1:[1,3]ADVENT.ODL')

    # Check file attributes
    print("\n=== File attributes comparison ===")
    dcl_cmd('DIR/FULL SY:[1,1]BP2IC2.ODL')
    dcl_cmd('DIR/FULL DM1:[1,3]ADVENT.ODL')

    # Try simpler overlay structure - maybe the problem is the syntax
    # Let me try a non-overlay build first
    print("\n=== Trying simpler TKB build without ODL ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Try building main program with just the object files linked together
    # This might fail if it's too big, but let's see
    child.sendline('DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,LB:BP2OTS/LB')
    idx = child.expect(['TKB>', 'FATAL', r'\$ '], timeout=30)

    if idx == 0:
        child.sendline('/')
        child.expect(['TKB>', 'Enter Options:'], timeout=30)
        child.sendline('')
        child.expect(r'\$ ', timeout=60)
    elif idx == 1:
        print("\n*** FATAL error ***")
        child.expect(['TKB>', r'\$ '], timeout=30)

    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    child.close()
    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
