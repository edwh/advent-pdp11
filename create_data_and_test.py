#!/usr/bin/env python3
"""Create data files and test ADVENT game."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create Data Files and Test ADVENT")
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

    # Delete old data files
    print("\n=== Deleting old data files ===")
    for dev in ['DM1:', 'SY:']:
        for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            dcl_cmd(f'DELETE/NOCONFIRM {dev}[1,2]{f}')

    # Create each data file in a separate BASIC session
    files_to_create = [
        ('ADVENT.DTA', 'R$(2000%)=512%'),
        ('ADVENT.MON', 'M$(10000%)=20%'),
        ('ADVENT.CHR', 'C$(100%)=512%'),
        ('BOARD.NTC', 'I%(511%),B$(511%)=512%'),
        ('MESSAG.NPC', 'N%(0%),S$(1000%)=60%'),
    ]

    for filename, dim_spec in files_to_create:
        print(f"\n=== Creating {filename} ===")
        child.sendline('RUN $BP2IC2')
        child.expect('BASIC2', timeout=15)

        child.sendline(f"OPEN 'DM1:[1,2]{filename}' AS FILE #1%, ACCESS SCRATCH, ALLOW NONE")
        child.expect('BASIC2', timeout=60)

        child.sendline(f'DIM #1%, {dim_spec}')
        child.expect('BASIC2', timeout=60)

        # Initialize first element
        if 'R$' in dim_spec:
            child.sendline('R$(1%)=STRING$(512%,32%)')
        elif 'M$' in dim_spec:
            child.sendline('M$(1%)=STRING$(20%,32%)')
        elif 'C$' in dim_spec:
            child.sendline('C$(1%)=STRING$(512%,32%)')
        elif 'B$' in dim_spec:
            child.sendline('I%(0%)=0%')
            child.expect('BASIC2', timeout=10)
            child.sendline('B$(1%)=STRING$(512%,32%)')
        elif 'S$' in dim_spec:
            child.sendline('N%(0%)=0%')
            child.expect('BASIC2', timeout=10)
            child.sendline('S$(1%)=STRING$(60%,32%)')
        child.expect('BASIC2', timeout=10)

        child.sendline('CLOSE #1%')
        child.expect('BASIC2', timeout=10)

        child.sendcontrol('z')
        child.expect(['BASIC2', r'\$ '], timeout=10)
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)

    # Verify data files
    print("\n=== Verifying data files ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Check ADVENT.TSK
    print("\n=== Checking ADVENT.TSK ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]ADVENT.TSK')

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
        'file',
        'Cannot',
        'Stop at',
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
        5: "FILE",
        6: "CANNOT",
        7: "STOPPED",
        8: "ERROR",
        9: "DCL PROMPT",
        10: "TIMEOUT"
    }

    print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    if idx in [0, 1, 2, 3, 4]:
        print("\n*** GAME IS STARTING! ***")
        time.sleep(3)
        # Try entering a name
        child.sendline('TEST')
        time.sleep(5)

    time.sleep(3)
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
