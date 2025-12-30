#!/usr/bin/env python3
"""Build ADVENT.TSK - very slow interactive entry of all lines."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Very Slow Line Entry")
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

    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Run TKB
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(2)

    # TKB input lines - same as the original TKB.CTL
    tkb_lines = [
        'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT/-',
        'DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR/-',
        'DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD/-',
        'DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE/-',
        'DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC/-',
        'DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP/-',
        'DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY,SY:[1,1]BP2OTS/LB',
    ]

    for i, line in enumerate(tkb_lines):
        print(f"\n>>> Line {i+1}/{len(tkb_lines)}: {line[:50]}...")
        child.sendline(line)

        # Wait a long time and check for TKB> prompt
        time.sleep(5)

        # Check what we get
        idx = child.expect(['TKB>', 'FATAL', 'error', 'syntax', 'Illegal', pexpect.TIMEOUT], timeout=30)
        print(f"\n*** Line {i+1} result: idx={idx} ***")

        if idx in [1, 2, 3, 4]:
            print(f"\n*** Error after line {i+1} ***")
            # Get more output
            time.sleep(2)
            print(f"Before: {child.before[-200:]}")
            break
        elif idx == 5:  # Timeout
            print("\n*** Timeout - may be OK, continuing ***")

    # If we got through all lines, end and handle options
    print("\n>>> Sending first /")
    child.sendline('/')
    time.sleep(3)

    done = False
    iterations = 0
    while not done and iterations < 10:
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

        print(f"\n*** Loop idx={idx} ***")

        if idx == 0:  # Enter Options
            child.sendline('')
            time.sleep(2)
        elif idx == 1:  # TKB>
            child.sendline('/')
            time.sleep(2)
        elif idx == 5:  # $
            done = True
        elif idx == 3:  # undefined
            print("\n*** Undefined symbols ***")
            child.expect('TKB>', timeout=60)
            child.sendline('/')
            time.sleep(2)
        elif idx in [2, 4, 6]:
            print(f"\n*** Error idx={idx} ***")
            done = True

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    child.sendline('DIR/SIZE DM1:[1,2]ADVENT.TSK')
    child.expect(r'\$ ', timeout=15)

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** SUCCESS! ADVENT.TSK created! ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
