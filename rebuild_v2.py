#!/usr/bin/env python3
"""Rebuild ADVENT.TSK - simpler approach."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Rebuild ADVENT.TSK - Simpler Approach")
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

    # Run TKB with all files linked together (no overlays)
    print("\n=== Running TKB ===")
    child.sendline('RUN $TKB')
    child.expect('TKB>', timeout=15)

    # Link all object files with BP2OTS library
    # Using continuation lines
    child.sendline('DM1:[1,2]ADVENT/FP,DM1:[1,2]ADVENT/-')
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVINI,DM1:[1,2]ADVOUT,DM1:[1,2]ADVNOR/-')
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVCMD,DM1:[1,2]ADVODD,DM1:[1,2]ADVMSG/-')
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVBYE,DM1:[1,2]ADVSHT,DM1:[1,2]ADVNPC/-')
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVPUZ,DM1:[1,2]ADVDSP,DM1:[1,2]ADVFND/-')
    child.expect('TKB>', timeout=30)

    child.sendline('DM1:[1,2]ADVTDY,SY:[1,1]BP2OTS/LB')
    child.expect('TKB>', timeout=30)

    # End input
    child.sendline('/')

    # Wait for options prompt
    idx = child.expect(['Enter Options:', 'TKB>', 'FATAL', 'error', r'\$ ', pexpect.TIMEOUT], timeout=60)
    if idx == 0:
        child.sendline('')  # Accept defaults
        idx = child.expect(['TKB>', r'\$ ', pexpect.TIMEOUT], timeout=120)
        if idx == 0:
            child.sendline('/')
            child.expect(r'\$ ', timeout=60)

    time.sleep(2)

    # Check for ADVENT.TSK
    print("\n=== Checking for ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

    # Assign devices
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
        'Cannot',
        'Stop',
        'ADVENT',
        'cave',
        'vast',
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
        5: "CANNOT",
        6: "STOPPED",
        7: "ADVENT MSG",
        8: "CAVERN",
        9: "VAST",
        10: "ERROR",
        11: "DCL PROMPT",
        12: "TIMEOUT"
    }

    print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    if idx in [0, 1, 2, 3, 4, 7, 8, 9]:
        print("\n*** Waiting for more... ***")
        time.sleep(5)

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
