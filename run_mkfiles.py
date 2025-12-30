#!/usr/bin/env python3
"""Run the MKFILES program to create data files."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Run MKFILES to Create Data Files")
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

    # Delete old files first
    print("\n=== Deleting old data files ===")
    for dev in ['DM1:', 'SY:']:
        for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            dcl_cmd(f'DELETE/NOCONFIRM {dev}[1,2]{f}')

    # Run BASIC
    print("\n=== Running BASIC to create files ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # OLD the saved program
    child.sendline('OLD "DM1:[1,2]MKFILES.B2S"')
    idx = child.expect(['BASIC2', 'Cannot', 'find'], timeout=15)

    if idx != 0:
        print("\n*** MKFILES.B2S not found, creating inline ***")
        # Create a simpler inline program
        lines = [
            '10 D$="DM1:[1,2]"',
            '20 PRINT "Creating ADVENT.DTA..."',
            '30 OPEN D$+"ADVENT.DTA" FOR OUTPUT AS FILE #1%',
            '40 FIELD #1%, 512% AS A$',
            '50 LSET A$=STRING$(512%,32%)',
            '60 FOR I%=1% TO 10%',
            '70 PUT #1%',
            '80 NEXT I%',
            '90 CLOSE #1%',
            '100 PRINT "ADVENT.DTA created"',
            '110 OPEN D$+"ADVENT.MON" FOR OUTPUT AS FILE #2%',
            '120 FIELD #2%, 20% AS M$',
            '130 LSET M$=STRING$(20%,32%)',
            '140 FOR I%=1% TO 10%',
            '150 PUT #2%',
            '160 NEXT I%',
            '170 CLOSE #2%',
            '180 PRINT "ADVENT.MON created"',
            '190 OPEN D$+"ADVENT.CHR" FOR OUTPUT AS FILE #3%',
            '200 FIELD #3%, 512% AS C$',
            '210 LSET C$=STRING$(512%,32%)',
            '220 FOR I%=1% TO 10%',
            '230 PUT #3%',
            '240 NEXT I%',
            '250 CLOSE #3%',
            '260 PRINT "ADVENT.CHR created"',
            '270 OPEN D$+"BOARD.NTC" FOR OUTPUT AS FILE #4%',
            '280 FIELD #4%, 514% AS B$',
            '290 LSET B$=STRING$(514%,32%)',
            '300 FOR I%=1% TO 10%',
            '310 PUT #4%',
            '320 NEXT I%',
            '330 CLOSE #4%',
            '340 PRINT "BOARD.NTC created"',
            '350 OPEN D$+"MESSAG.NPC" FOR OUTPUT AS FILE #5%',
            '360 FIELD #5%, 62% AS S$',
            '370 LSET S$=STRING$(62%,32%)',
            '380 FOR I%=1% TO 10%',
            '390 PUT #5%',
            '400 NEXT I%',
            '410 CLOSE #5%',
            '420 PRINT "MESSAG.NPC created"',
            '430 PRINT "Done!"',
            '440 END'
        ]
        for line in lines:
            child.sendline(line)
            time.sleep(0.1)
        child.expect('BASIC2', timeout=30)

    # Run the program
    print("\n=== Running the file creation program ===")
    child.sendline('RUN')

    # Wait for output
    time.sleep(5)
    idx = child.expect(['Done', 'created', 'Error', 'BASIC2', r'\$ ', pexpect.TIMEOUT], timeout=60)
    print(f"\n*** Program result: {idx} ***")

    # Exit BASIC
    child.sendcontrol('z')
    time.sleep(1)
    child.expect(['BASIC2', 'Ready', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check the files
    print("\n=== Checking files on DM1: ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Also check SY:
    print("\n=== Checking files on SY: ===")
    dcl_cmd('DIR/SIZE SY:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

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
