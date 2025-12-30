#!/usr/bin/env python3
"""Test the game properly and try to link more modules."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Test Game and Build Full TSK")
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

    # Run TEST.TSK and test the game more thoroughly
    print("\n=== Running TEST.TSK ===")
    child.sendline('RUN A:TEST')
    time.sleep(3)

    # Wait for : prompt
    idx = child.expect([':', r'\$ ', 'Error', 'trap', pexpect.TIMEOUT], timeout=30)
    print(f"\n*** Initial result: idx={idx} ***")

    if idx == 0:
        # Got game prompt! Try some commands
        print("\n*** Testing game commands ***")

        # Test LOOK
        child.sendline('LOOK')
        time.sleep(2)
        idx = child.expect([':', 'error', r'\$ ', pexpect.TIMEOUT], timeout=15)
        print(f"\n*** LOOK result: idx={idx} ***")

        if idx == 0:
            # Test HELP
            child.sendline('HELP')
            time.sleep(2)
            idx = child.expect([':', 'error', r'\$ ', pexpect.TIMEOUT], timeout=15)
            print(f"\n*** HELP result: idx={idx} ***")

        if idx == 0:
            # Try Ctrl+Z to exit cleanly
            child.sendcontrol('z')
            time.sleep(2)
            child.expect([r'\$ ', 'User:', pexpect.TIMEOUT], timeout=15)

    # Re-login if needed
    idx = child.expect(['User:', r'\$ ', pexpect.TIMEOUT], timeout=5)
    if idx == 0:
        child.sendline('[1,2]')
        child.expect('Password:', timeout=10)
        child.sendline('Digital1977')
        child.expect([r'\$ ', 'Job number'], timeout=15)
        if 'Job' in child.before:
            child.sendline('')
            child.expect(r'\$ ', timeout=10)

    # Now try building with more modules using /STRUCTURE
    print("\n=== Building with LINK /STRUCTURE ===")

    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.TSK')
    dcl_cmd('DELETE/NOCONFIRM A:ADVENT.MAP')

    # Use LINK with /STRUCTURE - handle prompts carefully
    child.sendline('LINK/BP2/STRUCTURE/EXECUTABLE=A:ADVENT/MAP A:')
    time.sleep(3)

    # Handle all prompts
    done = False
    prompt_count = 0
    while not done and prompt_count < 50:
        prompt_count += 1
        idx = child.expect([
            r'Root COMMON',
            r'Root files',
            r'Root PSECTs',
            r'Overlay:',
            r'\$ ',
            r'overflow',
            r'undefined',
            r'Error',
            pexpect.TIMEOUT
        ], timeout=30)

        print(f"\n*** Prompt {prompt_count}: idx={idx} ***")

        if idx == 0:  # Root COMMON areas
            # Empty for BP2
            child.sendline('')
            time.sleep(1)

        elif idx == 1:  # Root files
            # Minimal root - just main module
            child.sendline('A:ADVENT,A:ADVINI,A:ADVOUT')
            time.sleep(2)

        elif idx == 2:  # Root PSECTs
            child.sendline('')
            time.sleep(1)

        elif idx == 3:  # Overlay
            # Add remaining modules in overlays
            # Use flat structure - each overlay independent
            if prompt_count < 10:
                # Give first overlay modules
                child.sendline('A:ADVSHT,A:ADVFND,A:ADVDSP,A:ADVNPC')
                time.sleep(2)
            elif prompt_count < 15:
                child.sendline('A:ADVBYE,A:ADVPUZ,A:ADVTDY')
                time.sleep(2)
            elif prompt_count < 20:
                child.sendline('A:ADVMSG,A:ADVODD')
                time.sleep(2)
            elif prompt_count < 25:
                child.sendline('A:ADVNOR')
                time.sleep(2)
            elif prompt_count < 30:
                child.sendline('A:ADVCMD')
                time.sleep(2)
            else:
                # End overlays
                child.sendline('')
                time.sleep(2)

        elif idx == 4:  # $ prompt - done
            done = True

        elif idx == 5:  # overflow
            print("\n*** Overflow error ***")
            time.sleep(2)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
            done = True

        elif idx == 6:  # undefined
            print("\n*** Undefined symbols (continuing) ***")
            time.sleep(2)

        elif idx == 7:  # Error
            print("\n*** Error ***")
            time.sleep(2)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=30)
            done = True

        elif idx == 8:  # Timeout
            print("\n*** Timeout ***")
            child.sendline('')
            time.sleep(1)

    # Check result
    print("\n=== Checking ADVENT.TSK ===")
    child.sendline('DIR/SIZE A:ADVENT.TSK')
    time.sleep(2)
    child.expect([r'\$ ', pexpect.TIMEOUT], timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")

        # Run it
        print("\n=== Running ADVENT.TSK ===")
        child.sendline('RUN A:ADVENT')
        time.sleep(3)
        idx = child.expect([':', 'Error', 'trap', r'\$ ', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** ADVENT run: idx={idx} ***")
        if idx == 0:
            child.sendcontrol('z')
            time.sleep(2)
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
    else:
        print("\n*** ADVENT.TSK not created ***")
        # Check map for errors
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
