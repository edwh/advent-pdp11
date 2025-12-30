#!/usr/bin/env python3
"""Fix data files - copy to DM1: and create missing files."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Fix Data Files - Copy to DM1: and Create Missing")
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

    # Copy files from SY: to DM1:
    print("\n=== Copying files from SY: to DM1: ===")
    for f in ['ADVENT.MON', 'ADVENT.CHR']:
        dcl_cmd(f'DELETE/NOCONFIRM DM1:[1,2]{f}')
        dcl_cmd(f'COPY SY:[1,2]{f} DM1:[1,2]{f}')

    # Delete bad files
    print("\n=== Deleting bad BOARD.NTC and MESSAG.NPC ===")
    for dev in ['DM1:', 'SY:']:
        dcl_cmd(f'DELETE/NOCONFIRM {dev}[1,2]BOARD.NTC')
        dcl_cmd(f'DELETE/NOCONFIRM {dev}[1,2]MESSAG.NPC')

    # Create BOARD.NTC and MESSAG.NPC with correct sizes
    print("\n=== Creating BOARD.NTC ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create program for BOARD.NTC (512 bytes, not 514)
    lines = [
        '10 EXTEND',
        '20 ON ERROR GOTO 900',
        '30 D$="DM1:[1,2]"',
        '100 PRINT "Creating BOARD.NTC..."',
        "120 OPEN D$+'BOARD.NTC' FOR OUTPUT AS FILE #1%",
        '130 FIELD #1%, 512% AS B$',
        '140 LSET B$=STRING$(512%,0%)',
        '150 FOR I%=1% TO 100%',
        '160 PUT #1%',
        '170 NEXT I%',
        '180 CLOSE #1%',
        '190 PRINT "BOARD.NTC done"',
        '200 PRINT "Creating MESSAG.NPC..."',
        "220 OPEN D$+'MESSAG.NPC' FOR OUTPUT AS FILE #2%",
        '230 FIELD #2%, 62% AS N$',
        '240 LSET N$=STRING$(62%,0%)',
        '250 FOR I%=1% TO 100%',
        '260 PUT #2%',
        '270 NEXT I%',
        '280 CLOSE #2%',
        '290 PRINT "MESSAG.NPC done"',
        '800 PRINT "FILES CREATED!"',
        '810 END',
        '900 PRINT "Error:";ERR;"at line";ERL',
        '910 RESUME 800',
    ]

    for line in lines:
        child.sendline(line)
        time.sleep(0.2)

    time.sleep(2)

    # Run the program
    child.sendline('RUN')

    # Wait for completion
    while True:
        idx = child.expect([
            'FILES CREATED',
            'done',
            'Error:',
            'Ready',
            'BASIC2',
            pexpect.TIMEOUT
        ], timeout=60)

        if idx == 0:
            print("\n*** Files created! ***")
            break
        elif idx == 1:
            continue
        elif idx in [2, 3, 4, 5]:
            break

    time.sleep(1)

    # Exit BASIC
    child.sendcontrol('z')
    time.sleep(1)
    try:
        child.expect(['BASIC2', 'Ready', r'\$ '], timeout=10)
    except:
        pass
    child.sendcontrol('z')
    time.sleep(1)
    try:
        child.expect(r'\$ ', timeout=10)
    except:
        pass

    # Copy these files from SY: to DM1: as well
    print("\n=== Copying BOARD.NTC and MESSAG.NPC to DM1: ===")
    dcl_cmd('COPY SY:[1,2]BOARD.NTC DM1:[1,2]BOARD.NTC')
    dcl_cmd('COPY SY:[1,2]MESSAG.NPC DM1:[1,2]MESSAG.NPC')

    # Check all files
    print("\n=== Final file check on DM1: ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Test ADVENT
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
        'Cannot find',
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
        5: "CANNOT FIND",
        6: "STOPPED",
        7: "ERROR",
        8: "DCL PROMPT",
        9: "TIMEOUT"
    }

    print(f"\n*** Game result: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    if idx in [0, 1, 2, 3, 4]:
        print("\n*** GAME IS WORKING! ***")
        time.sleep(2)
        child.sendline('TEST')
        time.sleep(5)

    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
