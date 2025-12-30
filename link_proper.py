#!/usr/bin/env python3
"""Use LINK /STRUCTURE properly - understanding the prompts."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK using LINK /STRUCTURE (v2)")
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

    # Create logical name for shorter paths
    dcl_cmd('ASSIGN DM1:[1,2] A:')

    # Delete old TSK
    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.TSK')

    # Try LINK /STRUCTURE with all files
    print("\n=== Running LINK /STRUCTURE (all files) ===")
    # Format: LINK/BP2/STRUCTURE/EXECUTABLE=output file1,file2,...
    child.sendline('LINK/BP2/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:ADVENT')
    time.sleep(3)

    # Handle prompts properly
    done = False
    while not done:
        idx = child.expect([
            'Root COMMON',
            'Root files:',
            'Overlay:',
            r'\$ ',
            'Error',
            r'\?',
            pexpect.TIMEOUT
        ], timeout=60)

        print(f"\n*** idx={idx} ***")

        if idx == 0:  # Root COMMON areas
            # Accept default - just press enter
            child.sendline('')
            time.sleep(1)
        elif idx == 1:  # Root files
            # Root = ADVENT main program + essential init/output
            child.sendline('A:ADVENT,A:ADVINI,A:ADVOUT')
            time.sleep(2)
        elif idx == 2:  # Overlay
            # For flat overlay structure, don't use +
            # Each overlay group on separate prompt
            # Empty line ends overlay specification
            child.sendline('')  # End overlays - we'll use simpler structure
            time.sleep(1)
        elif idx == 3:  # $
            done = True
        elif idx in [4, 5]:  # Error
            print("\n*** Error ***")
            # Try to cancel
            child.sendcontrol('c')
            time.sleep(1)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
            done = True
        elif idx == 6:  # Timeout
            child.sendline('')
            time.sleep(1)

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")
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
