#!/usr/bin/env python3
"""Build ADVENT.TSK with minimal subroutines - only the essential ones."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Minimal Subroutines")
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

    # Delete old TSK
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Run TKB with only the essential subroutines
    # Based on the ADVENT.B2S main program, the essential calls are:
    # ADVINI (initialization), ADVOUT (output), ADVNOR (normal commands)
    # ADVCMD, ADVMSG
    print("\n=== Running TKB (minimal subroutines) ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # Try with only 5 subroutines + main + library = 7 files
    # Just 3 continuation lines
    tkb_lines = [
        # Line 1: Output, map, main + 2 subs
        'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI/-',
        # Line 2: 3 subs
        'DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD/-',
        # Line 3: 1 sub + library (no continuation - see if TKB processes this many)
        'DM1:[1,2]ADVMSG,SY:[1,1]BP2OTS/LB',
    ]

    for i, line in enumerate(tkb_lines):
        print(f"\n>>> [{i+1}/{len(tkb_lines)}] {line[:60]}...")
        child.sendline(line)
        time.sleep(2)

        idx = child.expect(['TKB>', 'FATAL', 'error', 'trap', 'undefined', pexpect.TIMEOUT], timeout=60)
        if idx == 1:
            print("\n*** FATAL error ***")
            child.sendcontrol('z')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
            return False
        elif idx == 3:
            print("\n*** Trap error ***")
            child.sendcontrol('z')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
            return False
        elif idx == 4:
            print("\n*** Undefined symbols (expected - missing subs) ***")
        elif idx == 5:
            print("\n*** Timeout ***")
            return False

    # Send / to end file input
    print("\n>>> Sending: /")
    child.sendline('/')
    time.sleep(2)

    # Wait for options prompt
    idx = child.expect(['Enter Options:', 'TKB>', 'FATAL', 'overflow', 'undefined', r'\$ ', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** After /: idx={idx} ***")

    if idx == 0:
        print("\n>>> Accepting defaults")
        child.sendline('')
        time.sleep(3)
        idx2 = child.expect(['TKB>', r'\$ ', 'overflow', 'undefined', pexpect.TIMEOUT], timeout=180)
        print(f"\n*** After options: idx2={idx2} ***")
        if idx2 == 0:
            child.sendline('/')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=120)
    elif idx == 1:
        child.sendline('/')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=120)
    elif idx == 4:
        print("\n*** Undefined symbols ***")
        child.expect('TKB>', timeout=60)
        child.sendline('/')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=60)

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! (partial build) ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
