#!/usr/bin/env python3
"""Create ALL data files fresh on DM1: - complete version."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create ALL Data Files on DM1: - Final Version")
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

    # First check what files exist
    print("\n=== Current files on DM1: ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Check if we need to recreate files with missing ones
    # Based on game requirements, we need all 5 files with non-zero size

    # Run BASIC to create/fix files
    print("\n=== Creating all data files ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create comprehensive program
    lines = [
        '10 EXTEND',
        '20 ON ERROR GOTO 900',
        '30 D$="DM1:[1,2]"',
        # ADVENT.DTA - check and create if needed
        '50 PRINT "Checking ADVENT.DTA..."',
        "60 OPEN D$+'ADVENT.DTA' FOR INPUT AS FILE #1%",
        '70 CLOSE #1%',
        '80 PRINT "ADVENT.DTA exists"',
        '90 GOTO 200',
        '100 PRINT "Creating ADVENT.DTA..."',
        "110 OPEN D$+'ADVENT.DTA' FOR OUTPUT AS FILE #1%",
        '120 FIELD #1%, 512% AS A$',
        '130 LSET A$=STRING$(512%,0%)',
        '140 FOR I%=1% TO 100%',
        '150 PUT #1%',
        '160 NEXT I%',
        '170 CLOSE #1%',
        '180 PRINT "ADVENT.DTA created"',
        # ADVENT.MON
        '200 PRINT "Checking ADVENT.MON..."',
        "210 OPEN D$+'ADVENT.MON' FOR INPUT AS FILE #2%",
        '220 CLOSE #2%',
        '230 PRINT "ADVENT.MON exists"',
        '240 GOTO 400',
        '250 PRINT "Creating ADVENT.MON..."',
        "260 OPEN D$+'ADVENT.MON' FOR OUTPUT AS FILE #2%",
        '270 FIELD #2%, 20% AS M$',
        '280 LSET M$=STRING$(20%,0%)',
        '290 FOR I%=1% TO 100%',
        '300 PUT #2%',
        '310 NEXT I%',
        '320 CLOSE #2%',
        '330 PRINT "ADVENT.MON created"',
        # ADVENT.CHR
        '400 PRINT "Checking ADVENT.CHR..."',
        "410 OPEN D$+'ADVENT.CHR' FOR INPUT AS FILE #3%",
        '420 CLOSE #3%',
        '430 PRINT "ADVENT.CHR exists"',
        '440 GOTO 600',
        '450 PRINT "Creating ADVENT.CHR..."',
        "460 OPEN D$+'ADVENT.CHR' FOR OUTPUT AS FILE #3%",
        '470 FIELD #3%, 512% AS C$',
        '480 LSET C$=STRING$(512%,0%)',
        '490 FOR I%=1% TO 100%',
        '500 PUT #3%',
        '510 NEXT I%',
        '520 CLOSE #3%',
        '530 PRINT "ADVENT.CHR created"',
        # BOARD.NTC
        '600 PRINT "Checking BOARD.NTC..."',
        "610 OPEN D$+'BOARD.NTC' FOR INPUT AS FILE #4%",
        '620 CLOSE #4%',
        '630 PRINT "BOARD.NTC exists"',
        '640 GOTO 800',
        '650 PRINT "Creating BOARD.NTC..."',
        "660 OPEN D$+'BOARD.NTC' FOR OUTPUT AS FILE #4%",
        '670 FIELD #4%, 512% AS B$',
        '680 LSET B$=STRING$(512%,0%)',
        '690 FOR I%=1% TO 100%',
        '700 PUT #4%',
        '710 NEXT I%',
        '720 CLOSE #4%',
        '730 PRINT "BOARD.NTC created"',
        # MESSAG.NPC
        '800 PRINT "Checking MESSAG.NPC..."',
        "810 OPEN D$+'MESSAG.NPC' FOR INPUT AS FILE #5%",
        '820 CLOSE #5%',
        '830 PRINT "MESSAG.NPC exists"',
        '840 GOTO 990',
        '850 PRINT "Creating MESSAG.NPC..."',
        "860 OPEN D$+'MESSAG.NPC' FOR OUTPUT AS FILE #5%",
        '870 FIELD #5%, 62% AS N$',
        '880 LSET N$=STRING$(62%,0%)',
        '890 FOR I%=1% TO 100%',
        '892 PUT #5%',
        '894 NEXT I%',
        '896 CLOSE #5%',
        '898 PRINT "MESSAG.NPC created"',
        '990 PRINT "ALL FILES READY!"',
        '995 END',
        # Error handler - create the missing file
        '900 E%=ERR',
        '905 IF E%=5% THEN RESUME 100 IF ERL=60%',
        '910 IF E%=5% THEN RESUME 250 IF ERL=210%',
        '915 IF E%=5% THEN RESUME 450 IF ERL=410%',
        '920 IF E%=5% THEN RESUME 650 IF ERL=610%',
        '925 IF E%=5% THEN RESUME 850 IF ERL=810%',
        '930 PRINT "Error:";E%;"at line";ERL',
        '940 RESUME 990',
    ]

    for line in lines:
        child.sendline(line)
        time.sleep(0.2)

    time.sleep(2)

    # Run the program
    print("\n=== Running program ===")
    child.sendline('RUN')

    # Wait for completion
    while True:
        idx = child.expect([
            'ALL FILES READY',
            'created',
            'exists',
            'Checking',
            'Error:',
            'Ready',
            'BASIC2',
            pexpect.TIMEOUT
        ], timeout=120)

        if idx == 0:
            print("\n*** All files ready! ***")
            break
        elif idx in [1, 2, 3]:
            continue  # Progress messages
        elif idx in [4, 5, 6]:
            break
        elif idx == 7:
            print("\n*** Timeout ***")
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

    # Check all files
    print("\n=== Final file check on DM1: ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC', timeout=30)

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
