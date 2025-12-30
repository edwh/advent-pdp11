#!/usr/bin/env python3
"""Build ADVENT.TSK with grouped files - fewer continuation lines."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Grouped Files (6 lines max)")
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

    # Run TKB
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)
    time.sleep(1)

    # Use only 5 continuation lines (line 6 is the library, no continuation)
    # Each line has 2-3 object files
    # Using D: for shorter device prefix (assigns already done)
    tkb_lines = [
        # Line 1: Output, map, main + 2 subs
        'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT=DM1:[1,2]ADVENT,DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT/-',
        # Line 2: 3 subs
        'DM1:[1,2]ADVNOR,DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD/-',
        # Line 3: 3 subs
        'DM1:[1,2]ADVMSG,DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT/-',
        # Line 4: 3 subs
        'DM1:[1,2]ADVNPC,DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP/-',
        # Line 5: 2 subs + library (no continuation)
        'DM1:[1,2]ADVFND,DM1:[1,2]ADVTDY,SY:[1,1]BP2OTS/LB',
    ]

    for i, line in enumerate(tkb_lines):
        print(f"\n>>> [{i+1}/{len(tkb_lines)}] Sending: {line}")
        child.sendline(line)
        time.sleep(2)  # Long delay between lines

        idx = child.expect(['TKB>', 'FATAL', 'error', 'trap', pexpect.TIMEOUT], timeout=60)
        if idx == 1:
            print("\n*** FATAL error ***")
            child.sendcontrol('z')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
            return False
        elif idx == 2:
            print("\n*** Error detected ***")
        elif idx == 3:
            print("\n*** Trap error ***")
            child.sendcontrol('z')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
            return False
        elif idx == 4:
            print("\n*** Timeout ***")
            return False

    # Send / to end file input
    print("\n>>> Sending: /")
    child.sendline('/')
    time.sleep(2)

    # Wait for options prompt
    idx = child.expect(['Enter Options:', 'TKB>', 'FATAL', 'overflow', r'\$ ', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** After /: idx={idx} ***")

    if idx == 0:
        # Accept defaults
        print("\n>>> Accepting defaults")
        child.sendline('')
        time.sleep(3)
        idx2 = child.expect(['TKB>', r'\$ ', 'overflow', pexpect.TIMEOUT], timeout=180)
        print(f"\n*** After options: idx2={idx2} ***")
        if idx2 == 0:
            child.sendline('/')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=120)
        elif idx2 == 2:
            print("\n*** Overflow error ***")
    elif idx == 1:
        child.sendline('/')
        child.expect([r'\$ ', pexpect.TIMEOUT], timeout=120)
    elif idx == 2:
        print("\n*** TKB FATAL ERROR ***")
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)
    elif idx == 3:
        print("\n*** Overflow ***")

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    if 'Total of' in child.before and 'blocks' in child.before:
        print("\n*** ADVENT.TSK exists! ***")

        dcl_cmd('ASSIGN DM1: DK1:')
        dcl_cmd('ASSIGN SY: DK0:')

        print("\n" + "=" * 60)
        print("TESTING ADVENT GAME")
        print("=" * 60)

        child.sendline('RUN DM1:[1,2]ADVENT')

        idx = child.expect([
            'Welcome',
            'What is your',
            'name',
            '>',
            'cave',
            'ADVENT',
            r'\?',
            r'\$ ',
            pexpect.TIMEOUT
        ], timeout=90)

        result_map = {
            0: "WELCOME",
            1: "NAME PROMPT",
            2: "NAME",
            3: "GAME PROMPT",
            4: "CAVERN",
            5: "ADVENT MSG",
            6: "ERROR",
            7: "DCL PROMPT",
            8: "TIMEOUT"
        }

        print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")
    else:
        print("\n*** ADVENT.TSK not found ***")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
