#!/usr/bin/env python3
"""Use LINK /STRUCTURE command to build ADVENT.TSK with overlays."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK using LINK /STRUCTURE")
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

    # Try LINK /STRUCTURE
    print("\n=== Running LINK /STRUCTURE ===")
    child.sendline('LINK/STRUCTURE/MAP A:ADVENT')
    time.sleep(2)

    # Handle prompts
    done = False
    iterations = 0
    while not done and iterations < 30:
        iterations += 1
        idx = child.expect([
            'Root files:',
            'Root PSECTs:',
            'Overlay:',
            'Files:',
            r'\$ ',
            'Error',
            'error',
            pexpect.TIMEOUT
        ], timeout=60)

        print(f"\n*** Link prompt idx={idx} ***")

        if idx == 0:  # Root files:
            # Main program + critical subroutines in root
            child.sendline('A:ADVENT,A:ADVINI,A:ADVOUT')
            time.sleep(2)
        elif idx == 1:  # Root PSECTs:
            # Just accept default
            child.sendline('')
            time.sleep(2)
        elif idx == 2:  # Overlay:
            # Send overlay groups
            # First overlay: ADVNOR, ADVCMD (largest modules)
            child.sendline('A:ADVNOR,A:ADVCMD+')
            time.sleep(2)
        elif idx == 3:  # Files:
            # This is the simple prompt, send all files
            child.sendline('A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVNOR,A:ADVCMD,A:ADVODD')
            time.sleep(2)
        elif idx == 4:  # $
            done = True
        elif idx in [5, 6]:  # Error
            print("\n*** Error during linking ***")
            done = True
        elif idx == 7:  # Timeout
            print("\n*** Timeout ***")
            # Try sending empty line
            child.sendline('')
            time.sleep(2)

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE A:ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")
        # Check map file for clues
        print("\n=== Checking for map file ===")
        dcl_cmd('DIR/SIZE A:ADVENT.MAP')

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
