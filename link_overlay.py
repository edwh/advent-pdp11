#!/usr/bin/env python3
"""Use LINK /STRUCTURE with proper overlay specification."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK with LINK /STRUCTURE overlays")
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

    # Delete old files
    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.TSK')

    # Run LINK with /STRUCTURE to get overlay prompts
    print("\n=== Running LINK /STRUCTURE ===")
    child.sendline('LINK/BP2/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:ADVENT')
    time.sleep(3)

    # Handle prompts
    overlay_num = 0
    done = False
    while not done:
        idx = child.expect([
            'Root COMMON',
            'Root files:',
            'Root PSECTs:',
            'Overlay:',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=60)

        print(f"\n*** idx={idx} ***")

        if idx == 0:  # Root COMMON areas
            # Usually empty for BP2
            child.sendline('')
            time.sleep(1)

        elif idx == 1:  # Root files
            # Put main program and essential modules in root
            # These stay in memory always
            child.sendline('A:ADVENT,A:ADVINI,A:ADVOUT')
            time.sleep(2)

        elif idx == 2:  # Root PSECTs
            # Accept default
            child.sendline('')
            time.sleep(1)

        elif idx == 3:  # Overlay
            overlay_num += 1
            if overlay_num == 1:
                # First overlay: command processing
                child.sendline('A:ADVNOR,A:ADVCMD')
                time.sleep(2)
            elif overlay_num == 2:
                # Second overlay: more commands
                child.sendline('A:ADVODD,A:ADVMSG')
                time.sleep(2)
            elif overlay_num == 3:
                # Third overlay: misc
                child.sendline('A:ADVBYE,A:ADVSHT,A:ADVNPC')
                time.sleep(2)
            elif overlay_num == 4:
                # Fourth overlay: puzzles/display
                child.sendline('A:ADVPUZ,A:ADVDSP,A:ADVFND,A:ADVTDY')
                time.sleep(2)
            else:
                # End overlays
                child.sendline('')
                time.sleep(2)

        elif idx == 4:  # $
            done = True

        elif idx == 5:  # Timeout
            print("\n*** Timeout ***")
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

        # Check the map file
        print("\n=== Map file ===")
        child.sendline('TYPE A:ADVENT.MAP')
        time.sleep(3)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
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
