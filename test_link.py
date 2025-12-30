#!/usr/bin/env python3
"""Test if undefined symbols are resolved at runtime from BP2RES.LIB."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Test LINK behavior with undefined symbols")
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

    # Install BP2RES
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Create logical name
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Check if TEST.TSK exists
    print("\n=== Checking TEST.TSK ===")
    child.sendline('DIR/SIZE A:TEST.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Try running TEST.TSK to see what happens
    print("\n=== Running TEST.TSK ===")
    child.sendline('RUN A:TEST')
    time.sleep(5)
    idx = child.expect(['trap', 'Error', 'error', ':', r'\$ ', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** Run TEST result: idx={idx} ***")

    if idx == 3:
        # Got : prompt - might be game input
        print("\n*** Got : prompt - game may be working! ***")
        child.sendline('QUIT')
        time.sleep(2)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
    elif idx == 4:
        print("\n*** Returned to $ prompt ***")
    else:
        # Send Ctrl+C
        child.sendcontrol('c')
        time.sleep(1)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Now try linking ALL modules with simple LINK (no overlays)
    # to see what undefined symbols there are
    print("\n=== Linking ALL modules (no structure) ===")
    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.TSK')
    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.MAP')

    child.sendline('LINK/BP2/EXECUTABLE=A:ADVENT/MAP A:ADVENT,A:ADVINI,A:ADVOUT')
    time.sleep(3)

    # Look for Files: prompt to add more
    idx = child.expect(['Files:', r'\$ ', 'overflow', pexpect.TIMEOUT], timeout=60)
    print(f"\n*** First link idx={idx} ***")

    if idx == 0:
        # Add more files
        child.sendline('A:ADVSHT,A:ADVFND,A:ADVDSP,A:ADVNPC,A:ADVBYE')
        time.sleep(3)
        idx = child.expect(['Files:', r'\$ ', 'overflow', pexpect.TIMEOUT], timeout=60)
        print(f"\n*** Second link idx={idx} ***")
        if idx == 0:
            child.sendline('A:ADVPUZ,A:ADVTDY,A:ADVMSG,A:ADVODD,A:ADVNOR,A:ADVCMD')
            time.sleep(5)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=120)

    # Check result
    print("\n=== Checking ADVENT.TSK ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK created! ***")
    else:
        print("\n*** No ADVENT.TSK ***")

    # Check map file for details
    print("\n=== Map file (first 50 lines) ===")
    child.sendline('TYPE/PAGE A:ADVENT.MAP')
    time.sleep(3)
    for _ in range(5):
        idx = child.expect(['Press RETURN', r'\$ ', pexpect.TIMEOUT], timeout=10)
        if idx == 0:
            child.sendline('')
            time.sleep(1)
        else:
            break

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
