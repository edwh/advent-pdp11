#!/usr/bin/env python3
"""Use LINK /STRUCTURE to build complete ADVENT.TSK with all modules."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build Complete ADVENT.TSK with LINK /STRUCTURE")
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

    # Delete old TSK
    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.TSK')

    # Run LINK with all files specified on command line
    # Don't use /STRUCTURE - just list all files
    print("\n=== Running LINK with all files ===")
    # Format: LINK/BP2 file1,file2,file3...
    child.sendline('LINK/BP2/EXECUTABLE=A:ADVENT/MAP A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVNOR,A:ADVCMD,A:ADVODD')
    time.sleep(3)

    # Check for prompts or completion
    idx = child.expect(['Files:', r'\$ ', 'overflow', 'undefined', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** First result: idx={idx} ***")

    if idx == 0:  # Files: prompt
        # Add more files
        child.sendline('A:ADVMSG,A:ADVBYE,A:ADVSHT,A:ADVNPC,A:ADVPUZ,A:ADVDSP,A:ADVFND,A:ADVTDY')
        time.sleep(3)
        child.expect([r'\$ ', 'overflow', pexpect.TIMEOUT], timeout=300)

    elif idx == 2:  # overflow
        print("\n*** Address overflow - need overlays ***")
    elif idx == 3:  # undefined
        print("\n*** Undefined symbols - continuing ***")
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=60)

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK created! ***")

        # Try to run it to see if it works
        print("\n=== Testing ADVENT.TSK ===")
        child.sendline('RUN A:ADVENT')
        time.sleep(5)
        idx = child.expect(['Error', 'error', 'trap', ':', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** Run result: idx={idx} ***")
        if idx == 3:
            # Got some output, try to exit
            child.sendcontrol('c')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
    else:
        print("\n*** ADVENT.TSK not found ***")

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
