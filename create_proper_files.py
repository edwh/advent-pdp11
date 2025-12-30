#!/usr/bin/env python3
"""Create proper data files with record allocation using PUT."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create Proper Data Files with Record Allocation")
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

    # Create a BASIC program to create the data files properly
    print("\n=== Creating MKFILES.B2S program ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Enter the program line by line
    program = '''10 EXTEND
20 ON ERROR GOTO 5000
30 D$="DM1:[1,2]"
40 PRINT "Creating ADVENT.DTA..."
50 OPEN D$+"ADVENT.DTA" FOR OUTPUT AS FILE #1%, RECORDSIZE 512%, ORGANIZATION RELATIVE FIXED
60 FIELD #1%, 512% AS A$
70 LSET A$=STRING$(512%,0%)
80 FOR I%=1% TO 100%
90 PUT #1%, RECORD I%
100 NEXT I%
110 CLOSE #1%
120 PRINT "Created ADVENT.DTA with 100 records"
200 PRINT "Creating ADVENT.MON..."
210 OPEN D$+"ADVENT.MON" FOR OUTPUT AS FILE #2%, RECORDSIZE 20%, ORGANIZATION RELATIVE FIXED
220 FIELD #2%, 20% AS M$
230 LSET M$=STRING$(20%,0%)
240 FOR I%=1% TO 100%
250 PUT #2%, RECORD I%
260 NEXT I%
270 CLOSE #2%
280 PRINT "Created ADVENT.MON with 100 records"
300 PRINT "Creating ADVENT.CHR..."
310 OPEN D$+"ADVENT.CHR" FOR OUTPUT AS FILE #3%, RECORDSIZE 512%, ORGANIZATION RELATIVE FIXED
320 FIELD #3%, 512% AS C$
330 LSET C$=STRING$(512%,0%)
340 FOR I%=1% TO 100%
350 PUT #3%, RECORD I%
360 NEXT I%
370 CLOSE #3%
380 PRINT "Created ADVENT.CHR with 100 records"
400 PRINT "Creating BOARD.NTC..."
410 OPEN D$+"BOARD.NTC" FOR OUTPUT AS FILE #4%, RECORDSIZE 514%, ORGANIZATION RELATIVE FIXED
420 FIELD #4%, 2% AS B1$, 512% AS B2$
430 LSET B1$=STRING$(2%,0%)
440 LSET B2$=STRING$(512%,0%)
450 FOR I%=1% TO 100%
460 PUT #4%, RECORD I%
470 NEXT I%
480 CLOSE #4%
490 PRINT "Created BOARD.NTC with 100 records"
500 PRINT "Creating MESSAG.NPC..."
510 OPEN D$+"MESSAG.NPC" FOR OUTPUT AS FILE #5%, RECORDSIZE 62%, ORGANIZATION RELATIVE FIXED
520 FIELD #5%, 2% AS N$, 60% AS S$
530 LSET N$=STRING$(2%,0%)
540 LSET S$=STRING$(60%,0%)
550 FOR I%=1% TO 100%
560 PUT #5%, RECORD I%
570 NEXT I%
580 CLOSE #5%
590 PRINT "Created MESSAG.NPC with 100 records"
600 PRINT
610 PRINT "All data files created successfully!"
620 GOTO 6000
5000 PRINT "Error:";ERR;"at line";ERL
5010 RESUME 6000
6000 END'''

    for line in program.split('\n'):
        if line.strip():
            child.sendline(line)
            time.sleep(0.2)

    time.sleep(1)
    child.expect('BASIC2', timeout=30)

    # Save the program
    child.sendline('SAVE "DM1:[1,2]MKFILES.B2S"')
    child.expect('BASIC2', timeout=30)

    # Run the program
    print("\n=== Running MKFILES to create data files ===")
    child.sendline('RUN')
    time.sleep(5)  # Give it time to create files

    # Wait for completion
    child.expect(['BASIC2', 'Ready', r'\$ '], timeout=120)

    # Exit BASIC
    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Check the files
    print("\n=== Checking created files ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')
    dcl_cmd('DIR/SIZE SY:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

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

    time.sleep(3)
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
