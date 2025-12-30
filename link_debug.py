#!/usr/bin/env python3
"""Debug linking - check map file and try /OTS=RESIDENT."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Debug Linking")
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

    # Check map file from last run
    print("\n=== Checking ADVGAM.MAP ===")
    child.sendline('TYPE A:ADVGAM.MAP')
    time.sleep(5)

    # Let map file output
    for _ in range(10):
        idx = child.expect(['Press RETURN', r'\$ ', pexpect.TIMEOUT], timeout=10)
        if idx == 0:
            child.sendline('')
            time.sleep(1)
        elif idx == 1:
            break
        else:
            break

    # Now try with /OTS=RESIDENT explicitly
    print("\n=== Linking with /OTS=RESIDENT ===")
    dcl_cmd('DELETE/NOCONFIRM A:ADVRES.TSK')

    child.sendline('LINK/BP2/OTS=RESIDENT/EXECUTABLE=A:ADVRES/MAP A:ADVENT,A:ADVINI,A:ADVOUT')
    time.sleep(5)

    idx = child.expect([r'\$ ', 'overflow', 'undefined', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** ADVRES result: idx={idx} ***")

    if idx == 2:
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Check result
    child.sendline('DIR/SIZE A:ADVRES.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before:
        print("\n*** ADVRES.TSK created ***")
        # Try running it
        child.sendline('RUN A:ADVRES')
        time.sleep(3)
        idx = child.expect(['#', ':', 'Error', r'\$ ', 'trap', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** Run result: idx={idx} ***")
        if idx in [0, 1]:
            child.sendline('LOOK')
            time.sleep(2)
            child.expect(['#', ':', r'\$ ', pexpect.TIMEOUT], timeout=15)
            child.sendcontrol('c')
            time.sleep(1)
            child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)

    # Check what SUBs are being called that aren't defined
    # Look at the source code ADVENT.B2S to understand dependencies
    print("\n=== Checking source file structure ===")
    child.sendline('DIR A:*.B2S')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    child.sendline('DIR A:*.SUB')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    # Check if there's an original .TSK or build files
    print("\n=== Looking for original build files ===")
    child.sendline('DIR A:*.ODL')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    child.sendline('TYPE A:ADVENT.ODL')
    time.sleep(3)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    # Re-login if needed
    idx = child.expect(['User:', r'\$ ', pexpect.TIMEOUT], timeout=5)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        child.expect([r'\$ ', 'Job'], timeout=15)

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
