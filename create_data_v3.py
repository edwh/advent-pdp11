#!/usr/bin/env python3
"""Create data files - use SY: then copy to DM1:."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create Data Files V3 - Create on SY: then copy to DM1:")
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

    # Delete old data files everywhere
    print("\n=== Deleting old data files ===")
    for dev in ['DM1:', 'SY:']:
        for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            dcl_cmd(f'DELETE/NOCONFIRM {dev}[1,2]{f}')

    # Create files using separate BASIC sessions
    # Use proper RSTS format: lower index for DIM
    files_to_create = [
        ('ADVENT.DTA', 'R$(0% TO 2000%)=512%', 'R$'),
        ('ADVENT.MON', 'M$(0% TO 10000%)=20%', 'M$'),
        ('ADVENT.CHR', 'C$(0% TO 100%)=512%', 'C$'),
    ]

    for filename, dim_spec, var_name in files_to_create:
        print(f"\n=== Creating {filename} on SY: ===")
        child.sendline('RUN $BP2IC2')
        child.expect('BASIC2', timeout=15)

        # Create on default device (SY:)
        child.sendline(f"OPEN '{filename}' AS FILE #1%, ACCESS SCRATCH, ALLOW NONE")
        child.expect('BASIC2', timeout=60)

        child.sendline(f'DIM #1%, {dim_spec}')
        child.expect('BASIC2', timeout=60)

        # Initialize element 0
        if '512' in dim_spec:
            child.sendline(f'{var_name}(0%)=STRING$(512%,32%)')
        else:
            child.sendline(f'{var_name}(0%)=STRING$(20%,32%)')
        child.expect('BASIC2', timeout=30)

        child.sendline('CLOSE #1%')
        child.expect('BASIC2', timeout=30)

        child.sendcontrol('z')
        child.expect(['BASIC2', r'\$ '], timeout=10)
        child.sendcontrol('z')
        child.expect(r'\$ ', timeout=10)

    # Create BOARD.NTC
    print("\n=== Creating BOARD.NTC on SY: ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)
    child.sendline("OPEN 'BOARD.NTC' AS FILE #1%, ACCESS SCRATCH, ALLOW NONE")
    child.expect('BASIC2', timeout=60)
    child.sendline('DIM #1%, I%(0% TO 511%),B$(0% TO 511%)=512%')
    child.expect('BASIC2', timeout=60)
    child.sendline('I%(0%)=0%')
    child.expect('BASIC2', timeout=30)
    child.sendline('CLOSE #1%')
    child.expect('BASIC2', timeout=30)
    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Create MESSAG.NPC
    print("\n=== Creating MESSAG.NPC on SY: ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)
    child.sendline("OPEN 'MESSAG.NPC' AS FILE #1%, ACCESS SCRATCH, ALLOW NONE")
    child.expect('BASIC2', timeout=60)
    child.sendline('DIM #1%, N%(0%),S$(0% TO 1000%)=60%')
    child.expect('BASIC2', timeout=60)
    child.sendline('N%(0%)=0%')
    child.expect('BASIC2', timeout=30)
    child.sendline('CLOSE #1%')
    child.expect('BASIC2', timeout=30)
    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check files on SY:
    print("\n=== Files created on SY: ===")
    dcl_cmd('DIR/SIZE SY:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Copy files from SY: to DM1:
    print("\n=== Copying files from SY: to DM1: ===")
    for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
        dcl_cmd(f'COPY SY:[1,2]{f} DM1:[1,2]{f}')

    # Verify on DM1:
    print("\n=== Files on DM1: ===")
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
        'Stop',
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
        5: "FILE MESSAGE",
        6: "CANNOT",
        7: "STOPPED",
        8: "ERROR",
        9: "DCL PROMPT",
        10: "TIMEOUT"
    }

    print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    # Capture any extra output
    time.sleep(2)
    try:
        child.expect(r'.', timeout=3)
    except:
        pass

    if idx in [0, 1, 2, 3, 4]:
        print("\n*** GAME IS STARTING! ***")
        time.sleep(3)
        child.sendline('TEST')
        time.sleep(5)
    elif idx == 8:
        # Error - let's see what the error was
        print("\n*** Error occurred - checking output ***")
        print(f"Before: {child.before}")
        print(f"After: {child.after}")

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
