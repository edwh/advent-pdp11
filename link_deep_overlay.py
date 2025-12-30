#!/usr/bin/env python3
"""Use LINK with deep nested overlays - each large module in its own segment."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK with Deep Nested Overlays")
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
    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.MAP')

    # First, let's check what LINK options are available
    print("\n=== Checking LINK help ===")
    child.sendline('HELP LINK')
    time.sleep(2)

    # Navigate through help pages
    for _ in range(5):
        idx = child.expect(['Topic', r'\$ ', 'Press RETURN', pexpect.TIMEOUT], timeout=10)
        if idx == 0:
            child.sendline('')  # Exit help
            break
        elif idx == 1:
            break
        elif idx == 2:
            child.sendline('')  # More
        else:
            child.sendline('')

    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    # Try LINK with just the smallest modules first to see if it works at all
    print("\n=== Testing LINK with small modules only ===")
    child.sendline('LINK/BP2/EXECUTABLE=A:TEST/MAP A:ADVENT,A:ADVINI,A:ADVOUT,A:ADVSHT')
    time.sleep(5)

    idx = child.expect([r'\$ ', 'overflow', 'undefined', 'Error', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** Small link result: idx={idx} ***")

    # Check if TEST.TSK was created
    child.sendline('DIR/SIZE A:TEST.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** Small TEST.TSK created! ***")
    else:
        print("\n*** Small TEST.TSK not created ***")

    # Now try with /STRUCTURE for deep nesting
    print("\n=== Running LINK /STRUCTURE with deep nesting ===")
    child.sendline('DELETE/NOCONFIRM A:ADVENT.TSK')
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)

    child.sendline('LINK/BP2/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:ADVENT')
    time.sleep(3)

    # Handle prompts - try putting ONLY main program in root
    # and EVERY other module in its own overlay
    overlay_count = 0
    done = False

    # Modules in order of size (smallest first in overlays)
    modules = [
        'A:ADVSHT',   # 5 blocks
        'A:ADVFND',   # 6 blocks
        'A:ADVOUT',   # 6 blocks
        'A:ADVINI',   # 11 blocks
        'A:ADVDSP',   # 14 blocks
        'A:ADVNPC',   # 20 blocks
        'A:ADVBYE',   # 23 blocks
        'A:ADVPUZ',   # 27 blocks
        'A:ADVTDY',   # 34 blocks
        'A:ADVMSG',   # 47 blocks
        'A:ADVODD',   # 50 blocks
        'A:ADVNOR',   # 98 blocks - largest
        'A:ADVCMD',   # 101 blocks - largest
    ]

    while not done:
        idx = child.expect([
            'Root COMMON',
            'Root files:',
            'Root PSECTs:',
            'Overlay:',
            r'\$ ',
            'Error',
            'overflow',
            pexpect.TIMEOUT
        ], timeout=60)

        print(f"\n*** idx={idx} ***")

        if idx == 0:  # Root COMMON areas
            child.sendline('')
            time.sleep(1)

        elif idx == 1:  # Root files
            # Put ONLY the main program in root - minimal footprint
            child.sendline('A:ADVENT')
            time.sleep(2)

        elif idx == 2:  # Root PSECTs
            child.sendline('')
            time.sleep(1)

        elif idx == 3:  # Overlay
            overlay_count += 1
            if overlay_count <= len(modules):
                # Each module in its own overlay
                module = modules[overlay_count - 1]
                print(f"\n*** Overlay {overlay_count}: {module} ***")
                child.sendline(module)
                time.sleep(2)
            else:
                # End overlays
                child.sendline('')
                time.sleep(2)

        elif idx == 4:  # $
            done = True

        elif idx in [5, 6]:  # Error or overflow
            print("\n*** Error/overflow ***")
            # Try to get more info
            time.sleep(2)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
            done = True

        elif idx == 7:  # Timeout
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
        # Show any errors in map
        child.sendline('TYPE A:ADVENT.MAP')
        time.sleep(3)
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)

    dcl_cmd('DEASSIGN A:')
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
