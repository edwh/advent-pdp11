#!/usr/bin/env python3
"""Build ADVENT.TSK with just 2 continuation lines - bare minimum test."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - 2 Lines Only (Minimal Test)")
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
    print("\n=== Installing BP2RES ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DELETE/NOCONFIRM SY:[1,2]ADVENT.TSK')

    # Run TKB with JUST 2 lines - main + library
    print("\n=== Running TKB (2 lines only) ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # Line 1: Output, map, main object file + continuation
    child.sendline('SY:[1,2]ADVENT/FP,SY:[1,2]ADVENT=SY:[1,2]ADVENT/-')
    time.sleep(2)
    idx = child.expect(['TKB>', 'FATAL', pexpect.TIMEOUT], timeout=60)
    if idx == 1:
        print("\n*** FATAL on line 1 ***")
        child.close()
        return False

    # Line 2: Just the library - no continuation
    child.sendline('SY:[1,1]BP2OTS/LB')
    time.sleep(2)
    idx = child.expect(['TKB>', 'FATAL', pexpect.TIMEOUT], timeout=60)
    if idx == 1:
        print("\n*** FATAL on line 2 ***")
        child.close()
        return False

    # End file input
    print("\n>>> Sending: /")
    child.sendline('/')
    time.sleep(2)

    # Handle options and linking
    done = False
    iterations = 0
    while not done and iterations < 10:
        iterations += 1
        idx = child.expect([
            'Enter Options:',
            'TKB>',
            'FATAL',
            'undefined',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=180)

        print(f"\n*** idx={idx} ***")

        if idx == 0:
            child.sendline('')
        elif idx == 1:
            child.sendline('/')
        elif idx == 4:
            done = True
        elif idx == 3:
            # Undefined symbols expected since we're missing subroutines
            print("\n*** Undefined symbols (expected) ***")
            child.sendline('')  # Accept anyway
        elif idx in [2, 5]:
            print("\n*** Error or timeout ***")
            done = True

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE SY:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! (main only, no subroutines) ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
