#!/usr/bin/env python3
"""Build ADVENT.TSK with minimal subroutines - test what links."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Minimal Link Test")
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
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Test: Just 3 object files + library = 2 input lines
    # Line 1: output/FP,map=main,sub1,sub2/-
    # Line 2: sub3,library/LB
    print("\n=== Running TKB (3 subs test) ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # Line 1: main + 3 most essential subroutines
    print("\n>>> Line 1: Main + ADVINI, ADVOUT, ADVNOR")
    child.sendline('DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI/-')
    time.sleep(3)
    idx = child.expect(['TKB>', 'FATAL', 'error', pexpect.TIMEOUT], timeout=60)
    if idx != 0:
        print(f"\n*** Error on line 1: idx={idx} ***")
        child.close()
        return False

    # Line 2: more subs + library
    print("\n>>> Line 2: ADVOUT, ADVNOR + library")
    child.sendline('DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,SY:[1,1]BP2OTS/LB')
    time.sleep(3)
    idx = child.expect(['TKB>', 'FATAL', 'error', pexpect.TIMEOUT], timeout=60)
    if idx != 0:
        print(f"\n*** Error on line 2: idx={idx} ***")
        child.close()
        return False

    # End input
    print("\n>>> Sending /")
    child.sendline('/')
    time.sleep(2)

    # Handle prompts
    done = False
    iterations = 0
    while not done and iterations < 15:
        iterations += 1
        idx = child.expect([
            'Enter Options:',
            'TKB>',
            'FATAL',
            'undefined',
            'overflow',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=180)

        print(f"\n*** idx={idx} ***")

        if idx == 0:
            child.sendline('')
        elif idx == 1:
            child.sendline('/')
        elif idx == 5:
            done = True
        elif idx == 3:
            print("\n*** Undefined symbols (expected - missing subs) ***")
            child.expect('TKB>', timeout=60)
            child.sendline('/')
        elif idx in [2, 4, 6]:
            print(f"\n*** Error idx={idx} ***")
            done = True

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
