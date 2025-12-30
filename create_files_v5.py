#!/usr/bin/env python3
"""Create data files using a BASIC program - with better handling."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create Data Files Using BASIC Program V5")
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

    # Delete existing files on both DM1: and SY:
    print("\n=== Deleting old data files ===")
    for dev in ['DM1:', 'SY:']:
        for f in ['ADVENT.DTA', 'ADVENT.MON', 'ADVENT.CHR', 'BOARD.NTC', 'MESSAG.NPC']:
            dcl_cmd(f'DELETE/NOCONFIRM {dev}[1,2]{f}')

    # Run BASIC
    print("\n=== Running BASIC and entering program ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Enter program lines
    program_lines = [
        '10 EXTEND',
        '20 ON ERROR GOTO 900',
        '30 D$="DM1:[1,2]"',
        '100 PRINT "Creating ADVENT.DTA..."',
        "120 OPEN D$+'ADVENT.DTA' FOR OUTPUT AS FILE #1%",
        '130 FIELD #1%, 512% AS A$',
        '140 LSET A$=STRING$(512%,0%)',
        '150 FOR I%=1% TO 100%',
        '160 PUT #1%',
        '170 NEXT I%',
        '180 CLOSE #1%',
        '190 PRINT "ADVENT.DTA done"',
        '200 PRINT "Creating ADVENT.MON..."',
        "220 OPEN D$+'ADVENT.MON' FOR OUTPUT AS FILE #2%",
        '230 FIELD #2%, 20% AS M$',
        '240 LSET M$=STRING$(20%,0%)',
        '250 FOR I%=1% TO 100%',
        '260 PUT #2%',
        '270 NEXT I%',
        '280 CLOSE #2%',
        '290 PRINT "ADVENT.MON done"',
        '300 PRINT "Creating ADVENT.CHR..."',
        "320 OPEN D$+'ADVENT.CHR' FOR OUTPUT AS FILE #3%",
        '330 FIELD #3%, 512% AS C$',
        '340 LSET C$=STRING$(512%,0%)',
        '350 FOR I%=1% TO 100%',
        '360 PUT #3%',
        '370 NEXT I%',
        '380 CLOSE #3%',
        '390 PRINT "ADVENT.CHR done"',
        '400 PRINT "Creating BOARD.NTC..."',
        "420 OPEN D$+'BOARD.NTC' FOR OUTPUT AS FILE #4%",
        '430 FIELD #4%, 514% AS B$',
        '440 LSET B$=STRING$(514%,0%)',
        '450 FOR I%=1% TO 100%',
        '460 PUT #4%',
        '470 NEXT I%',
        '480 CLOSE #4%',
        '490 PRINT "BOARD.NTC done"',
        '500 PRINT "Creating MESSAG.NPC..."',
        "520 OPEN D$+'MESSAG.NPC' FOR OUTPUT AS FILE #5%",
        '530 FIELD #5%, 62% AS N$',
        '540 LSET N$=STRING$(62%,0%)',
        '550 FOR I%=1% TO 100%',
        '560 PUT #5%',
        '570 NEXT I%',
        '580 CLOSE #5%',
        '590 PRINT "MESSAG.NPC done"',
        '800 PRINT "ALL FILES CREATED!"',
        '810 END',
        '900 PRINT "Error:";ERR;"at line";ERL',
        '910 RESUME 800',
    ]

    for line in program_lines:
        child.sendline(line)
        time.sleep(0.25)

    # Wait for all lines to be entered
    time.sleep(3)

    # Run the program
    print("\n=== Running program ===")
    child.sendline('RUN')

    # Wait for "Ready" or "ALL FILES" or timeout
    while True:
        idx = child.expect([
            'ALL FILES CREATED',
            'done',
            'Error:',
            'Ready',
            'BASIC2',
            pexpect.TIMEOUT
        ], timeout=60)

        if idx == 0:  # All files created
            print("\n*** SUCCESS: All files created! ***")
            break
        elif idx == 1:  # Saw "done"
            print("\n*** Progress: saw 'done' ***")
            continue
        elif idx == 2:  # Error
            print("\n*** ERROR in program ***")
            break
        elif idx == 3:  # Ready
            print("\n*** Program completed ***")
            break
        elif idx == 4:  # BASIC2 prompt
            print("\n*** At BASIC2 prompt ***")
            break
        elif idx == 5:  # Timeout
            print("\n*** Timeout waiting for program ***")
            break

    time.sleep(2)

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

    # Check files
    print("\n=== Checking files on DM1: ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC', timeout=30)

    print("\n=== Checking files on SY: ===")
    dcl_cmd('DIR/SIZE SY:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC', timeout=30)

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
