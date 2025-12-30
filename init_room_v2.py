#!/usr/bin/env python3
"""Initialize Room 1 with valid data - fixed version."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Initialize Room 1 with Valid Data V2")
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

    # Assign DK1: to DM1:
    dcl_cmd('ASSIGN DM1: DK1:')
    dcl_cmd('ASSIGN SY: DK0:')

    # Run BASIC to initialize room data
    print("\n=== Initializing Room 1 data ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create program to initialize room 1 - no newlines in strings
    lines = [
        '10 EXTEND',
        '20 ON ERROR GOTO 900',
        # Open ADVENT.DTA on DM1:
        "100 OPEN 'DM1:[1,2]ADVENT.DTA' AS FILE #1%, MODE 257%",
        '110 FIELD #1%, 1% AS ROOM$, 16% AS EX$, 83% AS PEOPLE$, 100% AS OBJECT$, 312% AS DESC$',
        # Initialize Room 1
        '200 GET #1%, RECORD 1%',
        '210 LSET ROOM$=CHR$(1%)',
        # Exits: N0001S0001E0001W0001 (all lead to room 1)
        '220 LSET EX$="N0001S0001E0001W001"',
        # Initialize PEOPLE$ - empty
        '230 LSET PEOPLE$=STRING$(83%,0%)',
        # Initialize OBJECT$ - empty
        '240 LSET OBJECT$=STRING$(100%,0%)',
        # Room description - simple, no newlines
        '250 D$="You are in a vast cavern. Exits lead in all directions."',
        '260 LSET DESC$=D$+STRING$(312%-LEN(D$),0%)',
        '270 PUT #1%, RECORD 1%',
        '280 PRINT "Room 1 initialized"',
        # Close and reopen files for other records
        '300 CLOSE #1%',
        "310 OPEN 'DM1:[1,2]ADVENT.CHR' AS FILE #2%, MODE 257%",
        '320 FIELD #2%, 512% AS C$',
        '330 GET #2%, RECORD 1%',
        '340 LSET C$=STRING$(512%,0%)',
        '350 PUT #2%, RECORD 1%',
        '360 CLOSE #2%',
        '370 PRINT "Character file initialized"',
        "400 OPEN 'DM1:[1,2]ADVENT.MON' AS FILE #3%, MODE 257%",
        '410 FIELD #3%, 20% AS M$',
        '420 GET #3%, RECORD 1%',
        '430 LSET M$=STRING$(20%,0%)',
        '440 PUT #3%, RECORD 1%',
        '450 CLOSE #3%',
        '460 PRINT "Monster file initialized"',
        '800 PRINT "ALL DATA INITIALIZED!"',
        '810 END',
        '900 PRINT "Error:";ERR;"at line";ERL',
        '910 RESUME 800',
    ]

    for line in lines:
        child.sendline(line)
        time.sleep(0.2)

    time.sleep(2)

    # Run the program
    print("\n=== Running initialization program ===")
    child.sendline('RUN')

    # Wait for completion
    while True:
        idx = child.expect([
            'ALL DATA INITIALIZED',
            'initialized',
            'Error:',
            'Ready',
            'BASIC2',
            pexpect.TIMEOUT
        ], timeout=60)

        if idx == 0:
            print("\n*** Initialization complete! ***")
            break
        elif idx == 1:
            continue
        elif idx in [2, 3, 4]:
            break
        elif idx == 5:
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
        9: "ERROR",
        10: "DCL PROMPT",
        11: "TIMEOUT"
    }

    print(f"\n*** Got: {result_map.get(idx, 'UNKNOWN')} (idx={idx}) ***")

    if idx in [0, 1, 2, 3, 4, 7, 8]:
        print("\n*** Waiting for more output... ***")
        time.sleep(3)
        try:
            idx2 = child.expect([r'name', 'Password', '>', r'\?', 'Welcome', 'cave', 'room', pexpect.TIMEOUT], timeout=30)
            print(f"\n*** Second expect: {idx2} ***")
        except:
            pass

        # Try entering a name
        print("\n*** Entering name 'HERO' ***")
        child.sendline('HERO')
        time.sleep(5)

        # Check result
        try:
            idx3 = child.expect(['Password', '>', 'Welcome', 'cave', 'vast', r'\?', pexpect.TIMEOUT], timeout=30)
            print(f"\n*** Third expect: {idx3} ***")
            if idx3 == 0:
                # Password prompt
                child.sendline('HERO')
                time.sleep(3)
                try:
                    idx4 = child.expect(['>', 'Welcome', 'cave', 'vast', r'\?', pexpect.TIMEOUT], timeout=30)
                    print(f"\n*** Fourth expect: {idx4} ***")
                except:
                    pass
        except:
            pass

    time.sleep(3)
    child.close()

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
    return True

if __name__ == '__main__':
    main()
