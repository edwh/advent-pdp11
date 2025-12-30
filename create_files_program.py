#!/usr/bin/env python3
"""Create data files using a proper BASIC program."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create Data Files Using BASIC Program")
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

    # Run BASIC and create a file creation program
    print("\n=== Creating file generation program ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Clear any old program
    child.sendline('NEW')
    child.expect('BASIC2', timeout=10)

    # Enter program lines - simpler program
    program_lines = [
        '10 EXTEND',
        '20 ON ERROR GOTO 900',
        '30 D$="DM1:[1,2]"',
        '100 REM CREATE ADVENT.DTA',
        '110 PRINT "Creating ADVENT.DTA..."',
        "120 OPEN D$+'ADVENT.DTA' FOR OUTPUT AS FILE #1%",
        '130 FIELD #1%, 512% AS A$',
        '140 LSET A$=STRING$(512%,0%)',
        '150 FOR I%=1% TO 100%',
        '160 PUT #1%',
        '170 NEXT I%',
        '180 CLOSE #1%',
        '190 PRINT "Done with ADVENT.DTA"',
        '200 REM CREATE ADVENT.MON',
        '210 PRINT "Creating ADVENT.MON..."',
        "220 OPEN D$+'ADVENT.MON' FOR OUTPUT AS FILE #2%",
        '230 FIELD #2%, 20% AS M$',
        '240 LSET M$=STRING$(20%,0%)',
        '250 FOR I%=1% TO 100%',
        '260 PUT #2%',
        '270 NEXT I%',
        '280 CLOSE #2%',
        '290 PRINT "Done with ADVENT.MON"',
        '300 REM CREATE ADVENT.CHR',
        '310 PRINT "Creating ADVENT.CHR..."',
        "320 OPEN D$+'ADVENT.CHR' FOR OUTPUT AS FILE #3%",
        '330 FIELD #3%, 512% AS C$',
        '340 LSET C$=STRING$(512%,0%)',
        '350 FOR I%=1% TO 100%',
        '360 PUT #3%',
        '370 NEXT I%',
        '380 CLOSE #3%',
        '390 PRINT "Done with ADVENT.CHR"',
        '400 REM CREATE BOARD.NTC',
        '410 PRINT "Creating BOARD.NTC..."',
        "420 OPEN D$+'BOARD.NTC' FOR OUTPUT AS FILE #4%",
        '430 FIELD #4%, 514% AS B$',
        '440 LSET B$=STRING$(514%,0%)',
        '450 FOR I%=1% TO 100%',
        '460 PUT #4%',
        '470 NEXT I%',
        '480 CLOSE #4%',
        '490 PRINT "Done with BOARD.NTC"',
        '500 REM CREATE MESSAG.NPC',
        '510 PRINT "Creating MESSAG.NPC..."',
        "520 OPEN D$+'MESSAG.NPC' FOR OUTPUT AS FILE #5%",
        '530 FIELD #5%, 62% AS N$',
        '540 LSET N$=STRING$(62%,0%)',
        '550 FOR I%=1% TO 100%',
        '560 PUT #5%',
        '570 NEXT I%',
        '580 CLOSE #5%',
        '590 PRINT "Done with MESSAG.NPC"',
        '800 PRINT "All files created!"',
        '810 END',
        '900 PRINT "Error:";ERR;"at line";ERL',
        '910 RESUME 800',
    ]

    for line in program_lines:
        child.sendline(line)
        time.sleep(0.15)

    time.sleep(1)

    # List the program to verify it was entered
    print("\n=== Program listing ===")
    child.sendline('LIST')
    time.sleep(3)
    child.expect(['BASIC2', 'Ready'], timeout=60)

    # Save the program
    print("\n=== Saving program ===")
    child.sendline('SAVE "DM1:[1,2]MKFILES"')
    child.expect('BASIC2', timeout=30)

    # Run the program
    print("\n=== Running program ===")
    child.sendline('RUN')

    # Wait for completion - allow time for file creation
    idx = child.expect(['All files created', 'Error', 'BASIC2', 'Ready', pexpect.TIMEOUT], timeout=120)
    print(f"\n*** Program execution result: {idx} ***")

    time.sleep(2)

    # Exit BASIC
    child.sendcontrol('z')
    child.expect(['BASIC2', 'Ready', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check files
    print("\n=== Checking files on DM1: ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

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
