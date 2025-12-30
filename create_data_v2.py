#!/usr/bin/env python3
"""Create data files properly with actual content allocation."""

import pexpect
import sys
import time

def main():
    print("=" * 60)
    print("Create Data Files V2 - With Proper Allocation")
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

    # Assign DK1: to DM1: (the game uses _DK1:)
    print("\n=== Assigning DK1: to DM1: ===")
    dcl_cmd('ASSIGN DM1: DK1:')

    # Create all data files using a single BASIC program with proper allocation
    print("\n=== Creating all data files with proper allocation ===")
    child.sendline('RUN $BP2IC2')
    child.expect('BASIC2', timeout=15)

    # Create ADVENT.DTA - 2000 records of 512 bytes each
    print("\n--- Creating ADVENT.DTA ---")
    child.sendline("OPEN 'DM1:[1,2]ADVENT.DTA' AS FILE #1%, ACCESS SCRATCH, ALLOW NONE")
    child.expect('BASIC2', timeout=60)

    child.sendline('DIM #1%, R$(2000%)=512%')
    child.expect('BASIC2', timeout=60)

    # Write to first and last elements to force allocation
    child.sendline('R$(1%)=STRING$(512%,32%)')
    child.expect('BASIC2', timeout=30)
    child.sendline('R$(100%)=STRING$(512%,32%)')
    child.expect('BASIC2', timeout=30)
    child.sendline('R$(2000%)=STRING$(512%,32%)')
    child.expect('BASIC2', timeout=30)

    child.sendline('CLOSE #1%')
    child.expect('BASIC2', timeout=30)
    print("*** ADVENT.DTA created ***")

    # Create ADVENT.MON - 10000 records of 20 bytes each
    print("\n--- Creating ADVENT.MON ---")
    child.sendline("OPEN 'DM1:[1,2]ADVENT.MON' AS FILE #2%, ACCESS SCRATCH, ALLOW NONE")
    child.expect('BASIC2', timeout=60)

    child.sendline('DIM #2%, M$(10000%)=20%')
    child.expect('BASIC2', timeout=60)

    # Write to first and last elements
    child.sendline('M$(1%)=STRING$(20%,32%)')
    child.expect('BASIC2', timeout=30)
    child.sendline('M$(5000%)=STRING$(20%,32%)')
    child.expect('BASIC2', timeout=30)
    child.sendline('M$(10000%)=STRING$(20%,32%)')
    child.expect('BASIC2', timeout=30)

    child.sendline('CLOSE #2%')
    child.expect('BASIC2', timeout=30)
    print("*** ADVENT.MON created ***")

    # Create ADVENT.CHR - 100 records of 512 bytes each
    print("\n--- Creating ADVENT.CHR ---")
    child.sendline("OPEN 'DM1:[1,2]ADVENT.CHR' AS FILE #3%, ACCESS SCRATCH, ALLOW NONE")
    child.expect('BASIC2', timeout=60)

    child.sendline('DIM #3%, C$(100%)=512%')
    child.expect('BASIC2', timeout=60)

    child.sendline('C$(1%)=STRING$(512%,32%)')
    child.expect('BASIC2', timeout=30)
    child.sendline('C$(100%)=STRING$(512%,32%)')
    child.expect('BASIC2', timeout=30)

    child.sendline('CLOSE #3%')
    child.expect('BASIC2', timeout=30)
    print("*** ADVENT.CHR created ***")

    # Create BOARD.NTC - integer array + string array
    print("\n--- Creating BOARD.NTC ---")
    child.sendline("OPEN 'DM1:[1,2]BOARD.NTC' AS FILE #4%, ACCESS SCRATCH, ALLOW NONE")
    child.expect('BASIC2', timeout=60)

    child.sendline('DIM #4%, I%(511%),B$(511%)=512%')
    child.expect('BASIC2', timeout=60)

    child.sendline('I%(0%)=0%')
    child.expect('BASIC2', timeout=30)
    child.sendline('B$(1%)=STRING$(512%,32%)')
    child.expect('BASIC2', timeout=30)
    child.sendline('B$(511%)=STRING$(512%,32%)')
    child.expect('BASIC2', timeout=30)

    child.sendline('CLOSE #4%')
    child.expect('BASIC2', timeout=30)
    print("*** BOARD.NTC created ***")

    # Create MESSAG.NPC - integer + string array
    print("\n--- Creating MESSAG.NPC ---")
    child.sendline("OPEN 'DM1:[1,2]MESSAG.NPC' AS FILE #5%, ACCESS SCRATCH, ALLOW NONE")
    child.expect('BASIC2', timeout=60)

    child.sendline('DIM #5%, N%(0%),S$(1000%)=60%')
    child.expect('BASIC2', timeout=60)

    child.sendline('N%(0%)=0%')
    child.expect('BASIC2', timeout=30)
    child.sendline('S$(1%)=STRING$(60%,32%)')
    child.expect('BASIC2', timeout=30)
    child.sendline('S$(1000%)=STRING$(60%,32%)')
    child.expect('BASIC2', timeout=30)

    child.sendline('CLOSE #5%')
    child.expect('BASIC2', timeout=30)
    print("*** MESSAG.NPC created ***")

    # Exit BASIC
    child.sendcontrol('z')
    child.expect(['BASIC2', r'\$ '], timeout=10)
    child.sendcontrol('z')
    child.expect(r'\$ ', timeout=10)

    # Verify data files
    print("\n=== Verifying data files on DM1: ===")
    dcl_cmd('DIR/SIZE DM1:[1,2]*.DTA,*.MON,*.CHR,*.NTC,*.NPC')

    # Also check SY: for any stray files
    print("\n=== Checking SY: for stray files ===")
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
