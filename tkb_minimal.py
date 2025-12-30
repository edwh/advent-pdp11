#!/usr/bin/env python3
"""Build ADVENT.TSK with minimal TKB commands - 2 files max per line."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Build ADVENT.TSK - Minimal TKB Method")
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
        time.sleep(0.3)

    # Install BP2RES
    print("\n=== Installing BP2RES library ===")
    child.sendline('RUN $UTLMGR')
    child.expect('Utlmgr>', timeout=15)
    child.sendline('INSTALL/LIBRARY SY:[0,1]BP2RES.LIB')
    child.expect('Utlmgr>', timeout=15)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Delete old TSK if exists
    dcl_cmd('DELETE/NOCONFIRM DM1:[1,2]ADVENT.TSK')

    # Run TKB - one file per line
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Use all object files on separate lines
    tkb_lines = [
        'DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT/-',
        'DM1:[1,2]ADVINI/-',
        'DM1:[1,2]ADVOUT/-',
        'DM1:[1,2]ADVNOR/-',
        'DM1:[1,2]ADVCMD/-',
        'DM1:[1,2]ADVODD/-',
        'DM1:[1,2]ADVMSG/-',
        'DM1:[1,2]ADVBYE/-',
        'DM1:[1,2]ADVSHT/-',
        'DM1:[1,2]ADVNPC/-',
        'DM1:[1,2]ADVPUZ/-',
        'DM1:[1,2]ADVDSP/-',
        'DM1:[1,2]ADVFND/-',
        'DM1:[1,2]ADVTDY/-',
        'SY:[1,1]BP2OTS/LB',
    ]

    for line in tkb_lines:
        print(f"\n>>> Sending: {line}")
        child.sendline(line)
        time.sleep(0.5)
        idx = child.expect(['TKB>', 'FATAL', 'error', 'trap', pexpect.TIMEOUT], timeout=30)
        if idx == 1 or idx == 2 or idx == 3:
            print(f"\n*** TKB Error on line: {line} ***")
            child.sendcontrol('z')
            child.expect([r'\$ ', pexpect.TIMEOUT], timeout=10)
            return False
        elif idx == 4:
            print("\n*** Timeout waiting for TKB> ***")
            return False

    # End file input
    print("\n>>> Sending: /")
    child.sendline('/')
    time.sleep(1)

    # Wait for options prompt
    idx = child.expect(['Enter Options:', 'TKB>', 'FATAL', r'\$ '], timeout=60)
    print(f"\n*** After /: idx={idx} ***")

    if idx == 0:
        # Accept defaults
        print("\n>>> Accepting default options")
        child.sendline('')
        time.sleep(2)
        idx2 = child.expect(['TKB>', r'\$ ', pexpect.TIMEOUT], timeout=120)
        print(f"\n*** After options: idx2={idx2} ***")
        if idx2 == 0:
            child.sendline('/')
            child.expect(r'\$ ', timeout=60)
    elif idx == 1:
        child.sendline('/')
        child.expect(r'\$ ', timeout=60)
    elif idx == 2:
        print("\n*** TKB FATAL ERROR ***")
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # Check if file exists in output
    if 'Total of' in child.before:
        print("\n*** ADVENT.TSK exists! ***")
    else:
        print("\n*** No ADVENT.TSK found ***")
        child.close()
        return False

    # Setup devices
    dcl_cmd('ASSIGN DM1: DK1:')
    dcl_cmd('ASSIGN SY: DK0:')

    # Test the game
    print("\n" + "=" * 60)
    print("TESTING ADVENT GAME")
    print("=" * 60)

    child.sendline('RUN DM1:[1,2]ADVENT')

    idx = child.expect([
        'Welcome',
        'What is your',
        'name',
        '>',
        'INITIALIZING',
        'cave',
        'vast',
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
        4: "INITIALIZING",
        5: "CAVERN",
        6: "VAST",
        7: "ADVENT MSG",
        8: "ERROR",
        9: "DCL PROMPT",
        10: "TIMEOUT"
    }

    print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    if idx in [0, 1, 2, 3, 4, 5, 6, 7]:
        print("\n*** Game started! Waiting for more... ***")
        time.sleep(5)

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
